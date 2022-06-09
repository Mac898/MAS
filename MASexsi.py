# ©Macauley Lim 2021 -- File Licensed Under The GNU GPLv3. See The Full Notice In License.md For Binding Terms.
import sys, MASsettings, argparse, time
from tools import pchelper, service_instance
#VMware imports
from pyVmomi import vim
from pyVim.task import WaitForTask
from tools.tasks import wait_for_tasks

settings = MASsettings.Settings()

VMPREFIX = settings.read("SETTINGS.EXSI.VMPREFIX")
VMRAM = settings.read("SETTINGS.EXSI.RAM")
VMCPU = settings.read("SETTINGS.EXSI.CPU")
VMDATA = settings.read("SETTINGS.EXSI.DATASTORE")
VMNET = settings.read("SETTINGS.EXSI.NETWORK")
VMDC = settings.read("SETTINGS.EXSI.DATACENTER")
VMISO = settings.read("SETTINGS.EXSI.ISOPATH")

args = argparse.ArgumentParser()
args.host = settings.read("SETTINGS.EXSI.IP")
args.user = settings.read("SETTINGS.EXSI.USER")
args.password = settings.read("SETTINGS.EXSI.PASS")
args.port = 443
args.disable_ssl_verification = True

si = service_instance.connect(args)

def create_config_spec(datastore_name, name):
    config = vim.vm.ConfigSpec()
    config.annotation = "Science Extension Project Virtual Machine. Do Not Touch 100% Automated"
    config.memoryMB = int(VMRAM)
    config.guestId = "ubuntu64Guest"
    config.name = name
    config.numCPUs = int(VMCPU)
    files = vim.vm.FileInfo()
    files.vmPathName = "["+datastore_name+"]"
    config.files = files
    return config

def GenerateVM(id):
    content = si.RetrieveContent()
    destination_host = pchelper.get_obj(content, [vim.HostSystem], "exsi1.local.HOME.NET")
    source_pool = destination_host.parent.resourcePool
    global VMDATA
    if VMDATA is None:
        VMDATA = destination_host.datastore[0].name
    config = create_config_spec(datastore_name=VMDATA, name=VMPREFIX+str(id))
    for child in content.rootFolder.childEntity:
        if child.name == VMDC:
            vm_folder = child.vmFolder
            break
        else:
            print("Datacenter %s not found!" % VMDC)
            sys.exit(1)
    try:
        WaitForTask(vm_folder.CreateVm(config, pool=source_pool, host=destination_host))
        print("VM created: %s" % id)
    except vim.fault.DuplicateName:
        print("VM duplicate name: %s" % id, file=sys.stderr)
    except vim.fault.AlreadyExists:
        print("VM name %s already exists." % id, file=sys.stderr)

def AddNIC(id):
    """
    :param si: Service Instance
    :param vm: Virtual Machine Object
    :param network_name: Name of the Virtual Network
    """
    network_name = VMNET
    content = si.RetrieveContent()
    search_index = si.content.searchIndex
    for child in content.rootFolder.childEntity:
        if child.name == VMDC:
            dc = child.vmFolder  # child is a datacenter
            break
        else:
            print("Datacenter %s not found!" % VMDC)
            sys.exit(1)

    vm = search_index.FindChild(dc, VMPREFIX+str(id))
    
    spec = vim.vm.ConfigSpec()
    nic_changes = []

    nic_spec = vim.vm.device.VirtualDeviceSpec()
    nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add

    nic_spec.device = vim.vm.device.VirtualE1000()

    nic_spec.device.deviceInfo = vim.Description()
    nic_spec.device.deviceInfo.summary = 'MASnet'

    network = pchelper.get_obj(content, [vim.Network], network_name)
    if isinstance(network, vim.OpaqueNetwork):
        nic_spec.device.backing = \
            vim.vm.device.VirtualEthernetCard.OpaqueNetworkBackingInfo()
        nic_spec.device.backing.opaqueNetworkType = \
            network.summary.opaqueNetworkType
        nic_spec.device.backing.opaqueNetworkId = \
            network.summary.opaqueNetworkId
    else:
        nic_spec.device.backing = \
            vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
        nic_spec.device.backing.useAutoDetect = False
        nic_spec.device.backing.deviceName = network_name

    nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    nic_spec.device.connectable.startConnected = True
    nic_spec.device.connectable.allowGuestControl = True
    nic_spec.device.connectable.connected = False
    nic_spec.device.connectable.status = 'untried'
    nic_spec.device.wakeOnLanEnabled = True
    nic_spec.device.addressType = 'assigned'
    nic_spec.device.addressType = vim.vm.device.VirtualEthernetCardOption.MacTypes.generated

    nic_changes.append(nic_spec)
    spec.deviceChange = nic_changes
    try:
        WaitForTask(vm.ReconfigVM_Task(spec=spec))
    except Exception as e:
        print(e)
    
    print("NIC CARD ADDED")

def new_cdrom_spec(controller_key, backing):
    connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    connectable.allowGuestControl = True
    connectable.startConnected = True

    cdrom = vim.vm.device.VirtualCdrom()
    cdrom.controllerKey = controller_key
    cdrom.key = -1
    cdrom.connectable = connectable
    cdrom.backing = backing
    return cdrom

def find_free_ide_controller(vm):
    for dev in vm.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualIDEController):
            # If there are less than 2 devices attached, we can use it.
            if len(dev.device) < 2:
                return dev
    return None

def find_device(vm, device_type):
    result = []
    for dev in vm.config.hardware.device:
        if isinstance(dev, device_type):
            result.append(dev)
    return result

def AddCD(id):
    iso = VMISO
    content = si.RetrieveContent()
    search_index = si.content.searchIndex
    for child in content.rootFolder.childEntity:
        if child.name == "ha-datacenter":
            dc = child.vmFolder  # child is a datacenter
            break
        else:
            print("Datacenter %s not found!" % "ha-datacenter")
            sys.exit(1)
    vm = search_index.FindChild(dc, VMPREFIX+str(id))
    cdrom_operation = vim.vm.device.VirtualDeviceSpec.Operation
    if iso is not None:
        device_spec = vim.vm.device.VirtualDeviceSpec()
        controller = find_free_ide_controller(vm)
        if controller is None:
            raise Exception('Failed to find a free slot on the IDE controller')
        backing = vim.vm.device.VirtualCdrom.IsoBackingInfo(fileName=iso)
        cdrom = new_cdrom_spec(controller.key, backing)
        device_spec.operation = cdrom_operation.add
        device_spec.device = cdrom
        config_spec = vim.vm.ConfigSpec(deviceChange=[device_spec])
        WaitForTask(vm.Reconfigure(config_spec))

        cdroms = find_device(vm, vim.vm.device.VirtualCdrom)
        cdrom = next(filter(lambda x: type(x.backing) == type(backing) and
                     x.backing.fileName == iso, cdroms))
        print("Added CD Rom")
    else:
        print('Skipping ISO test as no iso provided.')

def PowerOnVM(id):
    vmnames = [VMPREFIX+str(id)]
    content = si.RetrieveContent()
    obj_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.VirtualMachine],
                                                        True)
    vm_list = obj_view.view
    obj_view.Destroy()

    tasks = [vm.PowerOn() for vm in vm_list if vm.name in vmnames]

    wait_for_tasks(si, tasks)

def GetVMIPS(id):
    content = si.RetrieveContent()
    search_index = si.content.searchIndex
    for child in content.rootFolder.childEntity:
        if child.name == VMDC:
            dc = child.vmFolder  # child is a datacenter
            break
        else:
            print("Datacenter %s not found!" % VMDC)
            sys.exit(1)
    vm = search_index.FindChild(dc, VMPREFIX+str(id))
    ips = []
    for nic in vm.guest.net:
        addresses = nic.ipConfig.ipAddress
        for adr in addresses:
            ips.append(adr.ipAddress)
    return ips

def DeleteVM(id):
    print("Deleted VM")
    content = si.RetrieveContent()
    VM = pchelper.get_obj(content, [vim.VirtualMachine], VMPREFIX+str(id))
    wait_for_tasks(si, [VM.PowerOff()])
    time.sleep(3)
    wait_for_tasks(si, [VM.Destroy_Task()])

if __name__ == '__main__':
    #GenerateVM(1)
    AddNIC(1)
    AddCD(1)
    PowerOnVM(1)