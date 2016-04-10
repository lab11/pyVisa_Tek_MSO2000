
import matplotlib.pyplot as plt
import tekVisa

def main():
	tmp = tekVisa.getDeviceList()
	candidates = []
	for i in range(len(tmp)):
		if 'USB' in tmp[i]:
			candidates.append(tmp[i])
	while True:
		print('Discovered devices:')
		print('--------------------------------------------------------------')
		print('#\tID')
		for i in range(len(candidates)):
			print('{:}:\t{:}'.format(i, candidates[i]))
		devNum = input('Enter number to connect: ')
		if type(devNum)==int and devNum >= 0 and devNum < len(candidates):
			myDevice = tekVisa.scope(candidates[devNum])
			break
		else:
			print('Input Error')

	waveform = myDevice.get_waveform(['CH1', 'CH2', 'CH3'])

	# plot waveform
	fig, ax1 = plt.subplots()
	ax1.plot(waveform['time'], waveform['CH1'], 'b-')
	ax1.plot(waveform['time'], waveform['CH3'], 'r-')
	ax1.set_xlabel('time (s)')
	ax1.set_ylabel('voltage (v)', color='b')
	for tl in ax1.get_yticklabels():
	    tl.set_color('b')
	plt.grid()
	plt.show()
	

if __name__=='__main__':
	main()
