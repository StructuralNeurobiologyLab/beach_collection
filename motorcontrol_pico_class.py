import serial


COM_PORT = "COM6"  # Instrument port location
TIMEOUT = 1

class StepperValueError(Exception):
    pass

class SerialInstrument:
    def __init__(self,
                 port: str,
                 timeout: float | None = 1,
                 **serial_kwargs) -> None:
        self._connection = serial.Serial(
            port=port,
            timeout=timeout,
            write_timeout=timeout,
            **serial_kwargs
        )
        
    def write(self , direct : str , freq : int, degree: int):
        if freq < 0 or freq > 500:
            raise StepperValueError("Frequency out of range - must be between 0 and 500")
        elif direct != "left" and direct != "right":
            raise StepperValueError('Direction must be "left" or "right"')
        else:
            command = f'{{"direction": "{direct}", "freq": {freq}, "degree": {degree}}}'+"\n"
            self._connection.write(command.encode())
            return self._connection.readline().decode()
    
      
    def disconnect(self) -> None:
        self._connection.close()
        
        
        
if __name__ == "__main__":
    
    instrument = SerialInstrument(COM_PORT, TIMEOUT) # example - object Init, open Port
    print(instrument.write("left",8,60))			 # send instructions : direction, speed(Hz), angle in Deg
    instrument.disconnect()							 # close Port