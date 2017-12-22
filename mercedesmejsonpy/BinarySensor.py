from mercedesmejsonpy.vehicle import VehicleDevice

class ParkingSensor(VehicleDevice):
    def __init__(self, data, controller):
        super().__init__(data, controller)
        self.__state = False

        self.type = 'parking brake sensor'
        self.hass_type = 'binary_sensor'

        self.name = self._name()

        self.uniq_name = self._uniq_name()
        self.bin_type = 0x1
        self.update()

    def update(self):
        self._controller.update(self._id)
        data = self._controller.get_drive_params(self._id)
        if not data['ignitionState'] or data['ignitionState'] == 'LOCK':
            self.__state = True
        else:
            self.__state = False

    def get_value(self):
        return self.__state

    @staticmethod
    def has_battery():
        return False

