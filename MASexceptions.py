# ©Macauley Lim 2021 -- File Licensed Under The GNU GPLv3. See The Full Notice In License.md For Binding Terms.

class ClientNotAvailable(Exception):
    """Raised when the client is not found by ping testing."""

class ClientFailedProcess(Exception):
    """Raised when the client has failed some kind of sub-process. The SSH Server will now move to copy the log to the server's logs folder"""