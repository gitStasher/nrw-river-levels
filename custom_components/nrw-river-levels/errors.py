from homeassistant import exceptions

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate connection or other API issue."""    
class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate API authorisation failed (or has expired.)"""

