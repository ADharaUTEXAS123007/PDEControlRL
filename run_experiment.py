import spinup
from spinup import ppo_tf1, ppo_pytorch
import tensorflow as tf
import torch
import gym
from exp_map import exp_map
import time
import datetime
import actor_critic
import networks
import os


def assemble_path(sim_name, key, label, index):
	return 'output/%s/%s/%s_%02i' % (sim_name, key, label, index)

def get_path(sim_name, key, label):
	index = 0

	while os.path.isdir(assemble_path(sim_name, key, label, index)):
		index += 1
	
	return assemble_path(sim_name, key, label, index)

def run_experiment(sim_name='burger', key='00', epochs=500, save_freq=50, label=''):
	env_name = 'gym_phiflow:%s-v%s' % (sim_name, key)
	
	path = get_path(sim_name, exp_map[key], label)

	env_fn = lambda: gym.make(env_name)

	ac_kwargs = dict(
		activation=torch.nn.ReLU, device='cuda',
		pi_hidden_sizes=[4, 8, 16, 16, 16], pi_network=networks.ALT_UNET, 
		vf_hidden_sizes=[4, 8, 16, 16, 16], vf_network=networks.CNN_FUNNEL,
	)

	logger_kwargs = dict(output_dir=path, exp_name=sim_name)

	tic = time.time()
	ppo_pytorch(env_fn, ac_kwargs=ac_kwargs, steps_per_epoch=3200, epochs=epochs, logger_kwargs=logger_kwargs, 
			pi_lr=1e-5, vf_lr=1e-3, gamma=0.99, save_freq=save_freq, actor_critic=actor_critic.MLPActorCritic)
	toc = time.time()

	time_msg = 'Training time: %s' % datetime.timedelta(seconds=toc - tic)

	print(time_msg)

	with open('%s/training_stats.txt' % path, 'a') as file:
		file.write(time_msg)


run_experiment('burger', '20', 2000, 100, label="long_benchmark")
#run_experiment('navier', '314', 2000, 100, label='mod_unet')