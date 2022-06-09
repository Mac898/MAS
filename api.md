### ©Macauley Lim 2021 -- File Licensed Under The GNU GPLv3. See The Full Notice In License.md For Binding Terms.

# Routes

## Get Node ID /node
- GET
- MASclient
- Generate integer according to next available row
- Assign the NODEID to a random VPN_LOCATION from the VPN_LOCATIONS table assuming that the INSTANCES is less than the maximum 
- Increment the count of INSTANCES for that VPN_LOCATION by 1
- Put the assigned VPN_LOCATION in the Nodes table with the NODEID
- Assign the NODEID to a random STIMULUS from the STIMULI table assuming that the INSTANCES is less than the maximum 
- Increment the count of INSTANCES for that STIMULUS by 1
- Put the assigned STIMULUS in the Nodes table with the NODEID

## Send Results /results
- POST
- MASclient
- X-NODE-ID sends the node-id of the node
- Send python table of lines encoded with "," as delimiter
- Put into database as seperate columns (1-8) with X-NODE-ID as table UUID

## Apt Package List /aptpackages
- GET
- MASclient
- Returns a "," delimited list of apt packages to install

## Pip Package List /pippackages
- GET
- MASclient
- Returns a "," delimited list of pip packages to install for the Python 3 Component

## Send Errors /error
- POST
- MASclient/MASexsi
- X-NODE-ID sends the node-id of the node
- Content is a string containing the exception details.

## Get Commands /commands
- GET
- MASclient/MASexsi
- X-NODE-ID sends the node-id of the node
- Content is a list of COMMAND_IDENTIFIERs delimited by ","
- If NODES tables COMMAND_LIST are empty, then generate a new list of commands according to the template and the provided VPN_LOCATION.

## Complete Command /commands
- POST
- MASclient/MASexsi
- X-NODE-ID sends the node-id of the node
- Content is a COMMAND_IDENTIFIER
- Remove the appropriate COMMAND_IDENTIFIER from the X-NODE-ID Row's COMMAND_LIST

## Get Stimulus /stimulus
- GET
- MASclient
- X-NODE-ID sends the node-id of the node
- Content is a signal string comprising the text stimulus.
- Return the NODES tables STIMULUS

## Get VPN_LOCATION /vpnlocation
- GET
- MASclient
- X-NODE-ID sends the node-id of the node
- Content is a signal string comprising the text stimulus.
- Return the NODES tables VPN_LOCATION

# Command Identifiers (In Order)
- GenerateVM
- PushPayload
- RunPayload
- Install
- StartX
- JoinVPN
- LaunchFirefox
- RunAutoCompleteTest
- CloseFirefox
- LeaveVPN
- ShutdownLinux
- DeleteVM