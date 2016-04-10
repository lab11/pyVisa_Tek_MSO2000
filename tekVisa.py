
import visa
import unicodedata

RESOURCE_MANAGER = visa.ResourceManager()

def convUnicodeToAscii(s):
	return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')

def getDeviceList():
	tmp = list(RESOURCE_MANAGER.list_resources())
	tmp = [convUnicodeToAscii(i) for i in tmp]
	return tmp

class WaveformFormat(object):
	def __init__(self, preambleString):
		tmp = preambleString.split(';')
		tmp = [convUnicodeToAscii(i) for i in tmp]
		self.dictionary = {}

		for i in range(len(tmp)):
			if tmp[i] == '"s"':
				self.dictionary['Time multiplier'] = float(tmp[i+1])
			elif tmp[i] == '"V"':
				self.dictionary['Voltage multiplier'] = float(tmp[i+1])
				self.dictionary['Voltage Offset'] = float(tmp[i+2])
			elif 'Ch' in tmp[i]:
				channel_info = tmp[i].split(',')
				if 'mV' in channel_info[2]:
					tmpIdx = channel_info[2].index('mV')
					self.dictionary['Voltage Div'] = float(channel_info[2][:tmpIdx])/1000
				else:
					tmpIdx = channel_info[2].index('V')
					self.dictionary['Voltage Div'] = float(channel_info[2][:tmpIdx])

				if 'ms' in channel_info[3]:
					tmpIdx = channel_info[3].index('ms')
					self.dictionary['Time Div'] = float(channel_info[3][:tmpIdx])/1000
				else:
					tmpIdx = channel_info[3].index('s')
					self.dictionary['Time Div'] = float(channel_info[3][:tmpIdx])


class scope(object):
	def __init__(self, resource):
		self.myScope = RESOURCE_MANAGER.open_resource(resource)
	
	def checkChannel(self, channel):
		return True if channel == 'CH1' or channel == 'CH2' or channel == 'CH3' or channel == 'CH4' else False
	
	def set_channel(self, channel):
		if self.checkChannel(channel):
			#print('Set capture channel: {:}'.format(channel))
			self.myScope.write(':DAT:SOU '+channel)
		else:
			print('Error format, ex: set_channel(\'CH1\')')
	
	def get_channel(self):
		ch = convUnicodeToAscii(self.myScope.ask(':DAT:SOU?')).rstrip()
		print('Current capture channel: {:}'.format(ch))

	def acquire(self, start):
		if start=='ON':
			self.myScope.write(':ACQ:STATE ON')
		elif start=='OFF':
			self.myScope.write(':ACQ:STATE OFF')
		else:
			print('Error format, ex: acquire(\'ON/OFF\')')
	
	def get_waveform(self, channels):
		# stop acquisition
		self.acquire('OFF')
		waveform = {}
		for channel in channels:
			if self.checkChannel(channel):
				self.set_channel(channel)
				wave = self.myScope.query_binary_values('CURVe?', datatype='b', is_big_endian=True)
				preamble = WaveformFormat(self.myScope.ask(':WFMO?'))
				voltage = [(i - preamble.dictionary['Voltage Offset'])*preamble.dictionary['Voltage multiplier'] \
					for i in wave]
				if 'time' not in waveform:
					waveform['time'] = [i*preamble.dictionary['Time multiplier'] for i in range(len(voltage))]
				waveform[channel] = voltage
			else:
				print('Error format, ex: get_waveform(\'CH1\')')
		# restart acquisition
		self.acquire('ON')
		return waveform
	
	def get_channel_position(self, channel):
		if self.checkChannel(channel):
			self.set_channel(channel)
			preamble = WaveformFormat(self.myScope.ask(':WFMO?'))
			pos = float(self.myScope.ask(':'+channel+':POS?'))
			return preamble.dictionary['Voltage Div']*pos
		else:
			print('Error format, ex: get_channel_position(\'CH1\')')
			
	
	def set_channel_position(self, channel, v):
		if self.checkChannel(channel):
			self.set_channel(channel)
			preamble = WaveformFormat(self.myScope.ask(':WFMO?'))
			self.myScope.write(':'+channel+':POS '+str(float(v)/preamble.dictionary['Voltage Div']))
		else:
			print('Error format, ex: set_channel_position(\'CH1\', 0)')
	
	def get_volt_div(self, channel):
		if self.checkChannel(channel):
			return float(convUnicodeToAscii(self.myScope.ask(channel+':SCA?')).rstrip())
		else:
			print('Error format, ex: get_volt_div(\'CH1\')')

	def set_volt_div(self, channel, v_div):
		if self.checkChannel(channel) and v_div in {0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50}:
			self.myScope.write(channel+':SCA '+str(v_div))
		else:
			print('Error format, ex: set_volt_div(\'CH1\', 0.5)')
		
