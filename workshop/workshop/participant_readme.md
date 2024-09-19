
## Overview and Instructions

Every location you see the comment 

    #todo: #to-fill \
    ... some code ... \
    ................. \
    #todo: #to-fill
    
    block tag, can be an optional functions/code the participant will need to implement by itself. 

You need to implement the code.

*Use only built-in Python standard libraries to solve the workshop (no need for 3rd party libraries installed via PIP) 


### Connection flow
  * As the attackers, we assume the exploitation step already happened, and now we have an ability to run code on an infected endpoint
  * You will connect via SSH to the server and deploy your agent code there
* The agent side is acting as a bind TCP server, listening to incoming connection from the C2
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
- agent: code that will run on the agent(infected server) side
- c2: code that will run on the operator side (your computer), to control and give commands to the agent, with included CLI based UI. 
- protocol: code handling the implemented protocol structures and sockets on both the agent and c2 

### How to run:
#### Agent:
  - Run: agent_server.py <listening_port>

#### C2:
  - Run: ui.py <dst_ip> <dst_port>
  - c2.py receives commands to send to the agent, from your laptop, entered via ui.py, then receives and parse the response


*Each one of you have been assigned your own port number. Use ONLY this port number when you deploy your agent code in the server.

This port will be the one you should enter when connecting to the agent from ui.py using your laptop

*Each one of you have a folder based on your port number on the server side - please upload your code only to your folder!
For example if you received port 30000, your folder is /home/hackeriot/3000/<put your agent code here>


### Requirements

Required Knowledge for doing this workshop:
1. Basic Python experience, working with sockets and structs
2. Basic Network experience, working with TCP/IP protocols

Required tools from each participant:
1. Python3.8 or higher
2. SSH client (MobaXterm recommended) or some kind of public git account (github, gitlab etc...) in order to upload and pull agent's server code on the server

Recommended tools:
1. Pycharm

