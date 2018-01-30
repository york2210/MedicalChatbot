# -*- coding:utf-8 -*-

import time
import argparse
import pickle
import sys, os
sys.path.append(os.getcwd().replace("src/dialogue_system/run",""))

from src.dialogue_system.dialogue_manager import DialogueManager
from src.dialogue_system.agent import AgentRandom
from src.dialogue_system.agent import AgentDQN
from src.dialogue_system.agent import AgentRule
from src.dialogue_system.agent import AgentActorCritic
from src.dialogue_system.user_simulator import UserRule as User
from src.dialogue_system import dialogue_configuration

from src.dialogue_system.run import RunningSteward

parser = argparse.ArgumentParser()
parser.add_argument("--action_set", dest="action_set", type=str, default='./../data/action_set.p', help='path and filename of the action set')
parser.add_argument("--slot_set", dest="slot_set", type=str, default='./../data/slot_set.p', help='path and filename of the slots set')
parser.add_argument("--goal_set", dest="goal_set", type=str, default='./../data/goal_set.p', help='path and filename of user goal')
parser.add_argument("--disease_symptom", dest="disease_symptom", type=str, default="./../data/disease_symptom.p", help="path and filename of the disease_symptom file")
parser.add_argument("--max_turn", dest="max_turn", type=int, default=42, help="the max turn in one episode.")
parser.add_argument("--simulate_epoch_number", dest="simulate_epoch_number", type=int, default=500, help="the number of simulate epoch.")
parser.add_argument("--epoch_size", dest="epoch_size", type=int, default=100, help="the size of each simulate epoch.")
parser.add_argument("--evaluate_epoch_size", dest="evaluate_epoch_size", type=int, default=2000, help="the size of each simulate epoch when evaluation.")
parser.add_argument("--experience_replay_pool_size", dest="experience_replay_pool_size", type=int, default=10000, help="the size of experience replay.")
parser.add_argument("--gamma", dest="gamma", type=float, default=0.9, help="The discount factor of immediate reward.")
parser.add_argument("--hidden_size_dqn", dest="hidden_size_dqn", type=int, default=300, help="the hidden_size of DQN.")
parser.add_argument("--input_size_dqn", dest="input_size_dqn", type=int, default=494, help="the input_size of DQN.")
parser.add_argument("--warm_start", dest="warm_start",type=int, default=1, help="use rule policy to fill the experience replay buffer at the beginning, 1:True; 0:False")
parser.add_argument("--warm_start_epoch_number", dest="warm_start_epoch_number", type=int, default=10, help="the number of epoch of warm starting.")
parser.add_argument("--batch_size", dest="batch_size", type=int, default=16, help="the batch size when training.")
parser.add_argument("--log_dir", dest="log_dir", type=str, default="./../../../log/", help="directory where event file of training will be written, ending with /")
parser.add_argument("--epsilon", dest="epsilon", type=float, default=0.1, help="the greedy of DQN")
parser.add_argument("--train_mode", dest="train_mode", type=int, default=1, help="training mode? True:1 or False:0")
parser.add_argument("--checkpoint_path",dest="checkpoint_path", type=str, default="./../model/dqn/checkpoint/", help="the folder where models save to, ending with /.")
parser.add_argument("--performance_save_path",dest="performance_save_path", type=str, default="./../model/dqn/learning_rate/", help="the folder where learning rate save to, ending with /.")
parser.add_argument("--save_performance",dest="save_performance", type=int, default=1, help="save the performance? 1:Yes, 0:No")
parser.add_argument("--save_model", dest="save_model", type=int, default=1,help="save model? 1:Yes,0:No")
parser.add_argument("--saved_model", dest="saved_model", type=str, default="./../model/dqn/checkpoint/model_s0.79_r-51.95_t7.502_wd1.303_e25.ckpt")
parser.add_argument("--agent_id", dest="agent_id", type=int, default=1, help="the agent to be used:{0:AgentRule, 1:AgentDQN, 2:AgentActorCritic, 3:AgentRandom}")
parser.add_argument("--dqn_id", dest="dqn_id", type=int, default=3, help="the dqn to be used in agent:{0:initial dqn of qianlong, 1:dqn with one layer of qianlong, 2:dqn with two layers of qianlong, 3:dqn of Baolin.}")
parser.add_argument("--dialogue_file", dest="dialogue_file", type=str, default="./../data/dialogue_output/dialogue_file.txt", help="the file that used to save dialogue content.")
parser.add_argument("--save_dialogue", dest="save_dialogue", type=int, default=0, help="save the dialogue? 1:Yes, 0:No")
# For Actor-critic
parser.add_argument("--actor_learning_rate", dest="actor_learning_rate", type=float, default=0.001, help="the learning rate of actor")
parser.add_argument("--critic_learning_rate", dest="critic_learning_rate", type=float, default=0.001, help="the learning rate of critic")
parser.add_argument("--trajectory_pool_size", dest="trajectory_pool_size", type=int, default=100, help="the size of trajectory pool")

args = parser.parse_args()
parameter = vars(args)


def run():
    slot_set = pickle.load(file=open(parameter["slot_set"], "rb"))
    action_set = pickle.load(file=open(parameter["action_set"], "rb"))
    disease_symptom = pickle.load(file=open(parameter["disease_symptom"], "rb"))
    steward = RunningSteward(parameter=parameter)

    warm_start = parameter.get("warm_start")
    warm_start_epoch_number = parameter.get("warm_start_epoch_number")
    train_mode = parameter.get("train_mode")
    agent_id = parameter.get("agent_id")
    simulate_epoch_number = parameter.get("simulate_epoch_number")

    # Warm start.
    if warm_start == 1 and train_mode == 1:
        print("warm starting...")
        agent = AgentRule(action_set=action_set,slot_set=slot_set,disease_symptom=disease_symptom,parameter=parameter)
        steward.warm_start(agent=agent,epoch_number=warm_start_epoch_number)
    # exit()
    if agent_id == 1:
        agent = AgentDQN(action_set=action_set,slot_set=slot_set,disease_symptom=disease_symptom,parameter=parameter)
    elif agent_id == 2:
        agent = AgentActorCritic(action_set=action_set,slot_set=slot_set,disease_symptom=disease_symptom,parameter=parameter)
    elif agent_id == 3:
        agent = AgentRandom(action_set=action_set,slot_set=slot_set,disease_symptom=disease_symptom,parameter=parameter)
    elif agent_id == 0:
        agent = AgentRule(action_set=action_set,slot_set=slot_set,disease_symptom=disease_symptom,parameter=parameter)

    steward.simulate(agent=agent,epoch_number=simulate_epoch_number, train_mode=train_mode)


if __name__ == "__main__":
    run()