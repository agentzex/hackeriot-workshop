# Hackeriot Workshop


## Target
The participant will learn how malwares operate, in the post-exploitation step (https://attack.mitre.org/matrices/enterprise), focusing on the network communication side
and will build a simple agent and c2 system using Python.

## Overview and Instructions
### Main folders:
* workshop-solution folder: Has a full code solution to the workshop

* workshop folder: Has most of the code written, and other sections that are surrounded by 

    #todo: #to-fill \
    ... some code ... \
    ................. \
    #todo: #to-fill
    
    block tag, can be an optional functions/code the participant will need to implement by itself. 

*Use only built-in Python standard libraries to solve the workshop (no need for 3rd party libraries installed via PIP) 

*To make the workshop more challenging, you can hide some files(like a CTF flag) in the infected endpoint, and ask the participants to look for them and then upload them to their C2 using only their built solution.
### Connection flow
* Before starting the workshop, it's important to explain to the participants where in the attack flow (you can use the MITRE table) the attacker will use tools like this, how and why
  * As the attackers, we assume the exploitation step already happened, and now we have an ability to run code on an infected endpoint
  * This is where the workshop starts. The participants should already have access to the infected endpoint and the ability to upload and execute their solution.
  * This can be via SSH or other.
* The agent side is acting as a bind TCP server, listening to incoming connection from the C2
  - In real life scenarios  the agent will probably be connect via reverse TCP connection, but for simplicity and FW constraints
  (also to enable running the agent in a cloud VM), this isn't the case here.

* The C2 side will act as TCP client, connecting to the agent's server and controlling it.

The overall flow from both sides in high level:

1. C2 (acting as client) ->TCP CONNECT ->  agent(acting as server)
     handshake starts
2. agent sends agent_hello() -> C2 receives and perform agent init
     (checks if uuid allowed to communicate with C2, create output dir etc)
     handshake completes
3. C2 sends c2_hello() -> agent receives connect request success/fail
    if fail -> agent exit
    if success -> agent waits for incoming commands
4. Agent gains persistency on server via cron (allow server to start if not already started)
5. C2 receives commands from user's UI and send to agent
6. agent executes and sends response to C2



#### Folders structure:
- agent: code that will run on the agent(infected endpoint) side
- c2: code that will run on the operator side, to control and give commands to the agent, with included CLI based UI. 
- protocol: code handling the implemented protocol structures and sockets on both the agent and c2 

### How to run:
#### Agent:
  - Run: agent_server.py <listening_port>
- The agent side was written with Linux (as the infected endpoint) in mind and was only tested on Linux machines.
  - Acting as a bind multithreaded (need to be enabled) TCP server
  - It can be run from a Linux VM, or in a docker container - you can use ubuntu_docker_run.py to start one (It has built-in SSH server for connection).
  - If needed, it should be easy to port some of the OS specific code in order to run the agent on a Windows or macOS machine as well

#### C2:
  - Run: ui.py <dst_ip> <dst_port>
  - Acting as a TCP client
  - The c2 side should be running from the participant's laptop
  - c2.py receives commands to send to the agent, from the operator (the participant), entered via ui.py, then receives and parse the response

Additional functionalities, protocols and abilities for the agent to execute can be added.\
After adding new ability, add its function handler to the function handler dictionaries in both the agent and c2 code.
It will then be automatically added also to the C2 UI.

### Requirements

Required Knowledge for doing this workshop:
1. Basic Python experience, working with sockets and structs
2. Basic Network experience, working with TCP/IP protocols

Required tools from each participant:
1. Python3.8 or higher
2. SSH client (MobaXterm recommended) or some kind of public git account (github, gitlab etc...) in order to upload and pull agent's server code on the cloud VM

Recommended tools:
1. Pycharm or other preferred IDE

