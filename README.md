# OctoSprings

* This is a model of an octopus arm based on the work by Yekutieli et al 

* There are 20 segments defined by point masses connected by springs
	* The springs connect every segment of four points to make a box with an X in the middle
	* The perpendicular and X springs are not directly controllable, and are used to support the arm so that it does not fold in on itself. They are thus stronger than other springs
	* Springs are dampened in order to simulate a Maxwell Fluid so that the arm does not oscillate forever, as it is controlled

* The top and bottom springs can be controlled by pressing keys
	* Each key controls 2 springs
		* So pressing q makes the fist and second springs on the top contract, pressing w makes the third and fourth springs contract etc.
		* Keys a to ; control the bottom row

* The goal is to touch the red target points as many times as possible. This is also what the neural network will be trained up to do over time. 

* Running this requires Pygame to run, which can be obtained by running 'pip install pygame'
	* If you do not have pip run 'sudo easy_install pip'
		
