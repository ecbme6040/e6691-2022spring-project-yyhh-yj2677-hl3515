# Dynamic-Grasping-Meta-Controller:alarm_clock:

## Weekly Log 🦾:

### 04/12/2022 Meeting9:
**Update / Current Result**
* Current training set up:
  * Fixed scene; Fixed grasp pose; Random initialize start pose (red cube range)

<div align=center>
<img src='Pictures/04_12/sample1.gif' width="400" height="300">
</div>
  
  * Benchmark results / 100 trials / 4th scene / 8th grasp pose

      | Time Budget/s    | Success Rate | Average Time/s |
      |--------|----------|----------|
      | 0.025s | 73% | 2.36778 |
      | 0.2s   | 92% | 1.9639 |
      | 0.5s | 88% | 2.66411 |
      | 2s     | 74% | 5.99543 |

* Single episode (9th); planned time by each step
<div align=center>
<img src='Pictures/04_12/index_9_time_steps.png' width="400" height="300">
</div>
In each subplot, the x axis is time steps, y axis is planned time in this step, and title shows the time-budget and success (True or False).

* Training results update <br>
Learning rate: 0.5e-4; Entropy: 0.05; Batch size: 1000; Discount: 1
<div align=center>
<img src='Pictures/04_12/Critic_Loss.png' width="400" height="300">
<img src='Pictures/04_12/Policy Loss.png' width="400" height="300">
<img src='Pictures/04_12/Reward_train.png' width="400" height="300">
</div>

After tuning parameters, the performance gets a bit increase.

**Questions**
* Speed up the training environment. Current one is too slow. 
* Add one more action: planning time prediction (where to start at next plan step) based on same observation

**Summary & TODO**
* Github repository clean up for collaboration
* Plot fixed: running reward (after 100 trials); reward scaling
* Train more and speed up training process
  * Remove p.resetsimulation() and not reload urdf but only use reset
  * Multiple environment for training maybe (low priority)

### 03/25/2022 Meeting8 & Stage Summary:flags:
**Update / Curruent Result**
* RRT and RRT* implementation and comparison
* Two environment setup: Normal Obstacles(3 different obstacles); Top shelf obstacle
  * Normal Obstacles: RRT gets best 91% at 0.025s time budget while RRT* gets best 79% at 0.5s time budget
  * Top Shelf: RRT gets best 80% at 0.2s time budget while RRT* gets best 59% at 1s time budget
  * The distribution shows that by increasing the time-budget, the cases of using all time become fewer. However, there are some steps may not exist solution (The most right column of each distribution is still high), meaning instead of using all time at this step to plan a non-exist solution, controller needs to constraint a small time-budget to let robotic arm start at a new pose and target not move too far.<br>


                                       -Normal Obstacles-

<div align=center>
<img src='Pictures/03_27/Normal Obstacles.png' width="400" height="300">
</div>
                 

<div align=center>
<img src='Pictures/03_27/RRT_normal_obs_300trials.png' width="400" height="300">
<img src='Pictures/03_27/RRT_star_normal_obs_100trials.png' width="400" height="300">
</div>

                        RRT 100 Trials                                 RRT* 100 Trials
<br>

                                             -Top Shelf Obstacle-

<div align=center>
<img src='Pictures/03_27/Top shelf obstacle.png' width="400" height="300">
</div>



<div align=center>
<img src='Pictures/03_27/RRT_top_shelf_100trials.png' width="400" height="300">
<img src='Pictures/03_27/RRT_star_top_shelf_100trials.png' width="400" height="300">
<img src='Pictures/03_27/RRT_top_shelf_distribution.png' width="400" height="300">
<img src='Pictures/03_27/RRT_star_top_shelf_distribution.png' width="400" height="300">
</div>

                        RRT 100 Trials                                 RRT* 100 Trials

* Training--Normal 3 Obstacles & RRT planner
  * Object: Meta controller should solve two cases:
    * Constraint to small time-budget when recognize there is no path
    * Set large time-budget when arm needs to go over the local minimum (shown in Meeting7's gif)
  * States: Distance between eef with the target (1 para) + eef pose (7 para) + target pose (7 para) + 3 obstacles pose (21 para)
  * Action: Time budget (1 continuous scalar; range setting 0s~3s)
  * Model: SAC with fully-connected layers (need GRU maybe)
  * Evaluation: Running average of success 
  * Online training with random scene setting (need to offline training first, then online training)

**Questions**<br>
* Why RRT* performance is worse than RRT?
  * Our planner is currently direct path planner with RRT / RRT* guidance and execute a part of planned path based on arm maximum velocity. Our environment is totally dynamic.
  * More time used to optimize planned trajectory does not contribute to improvement but even get worse performance: the prediction duration is based on the distance between gripper with target rather than time-budget, and we do not know how much time would be used in this plan step. RRT* would get stuck there to optimize an old path where the target might already move forward, while RRT could quickly adjust its pose to get closer to the target and finally use direct path.
* How to move the arm when a success plan is not found given the time budget?  
  * Currently because our planner is Greedy RRT, when the time budget is used up, planner will return the last explored path to execute. This randomness (plan in a new start position) could a bit improve the performance instead of stucking there or return the closest path.
* How to train:
  * What states that we should include and assume we have if we want to design a visual based meta controller? Obstacles 3-D bounding box? 
  * How to design the reward function to satisfy our objective of meta controller?
  * How to guarantee generalization, if transfers to other task?

**Summary**
* HTML visualize: completed path (scene + time) record images to offer intuition when meta controller needs larger time-budget
* Use running average success rate as training evaluation; 100 trials as test
* Replace tensorboard with wandb
* Prepare for a meeting next week to talk about how to train in details!!
  

### 03/11/2022 Meeting7 - 03/16/2022
**Update**<br>

* RRT* has now been implemented to compare with RRT planner especially in the shelf scene
* Constraint mode has been updated to avoid physical simulation unstable performance in lift execution
* Fix the bugs of RRT and fine tune the pipeline (ikfast for goal joint search; ikpybullet for lift execution). The grasp success rate has increased to 90% with obstacles.<br>
* Smooth the trajectory plan to guarantee robot arm would move to the planned point by given time step.
* Visualize the planned path using different time-budget in one grasp episode. Find some cases that robot need to quickly adjust their pose for next plan (change their starting point) rather than being stuck.
\[Current Results\] link: https://github.com/Ys-Jia/Dynamic-Grasping-Meta-Control/blob/main/Pictures/3.11-motion-time.pdf


**Questions**<br>

* Unstable lift performance: need to create constraint rather than physical simulation to better check controller performance (has been fixed!).
* Start pose collision problem: if the gripper gets touch with the target during movement, it would get stuck in next plan(low priority to fix, or would meta controller avoid this performance)?
* Large time-budget needed to escape the 'local minimum'
<div align=center>
<img src='Pictures/03-16-large time needed.gif' width="400" height="300">
</div>

**Summary**<br>
* Implement RRT* planner to compare with RRT performance (Already, results are collecting).
* Compare RRT greedy/not greedy performance.
* Add top slap to constraint the direct path planning (increase difficulty)!
* Set up server to quicker generate data and results.

### 03/04/2022 Meeting6
**Update**<br>
1. Fixed prediction bug, RRT path bug (as shown in the picture below, the trajectory now is continuous), adjust prediction duration, success rate increase above 80% (0.1 time-budget); Now for motion planning we use ikfast, while for lift execution we use ik pybullet.<br>
\[Current Results\] link: https://github.com/Ys-Jia/Dynamic-Grasping-Meta-Control/blob/main/Pictures/3.8-motion-time.pdf
3. find different modules will affect success rate: 
   switch on/off always grasp pose changing | different durations target pose prediction: 2s, 1s, 0s | Whether use future pose or not 
2. Add obstacles in the scene; Large time-budget seems get benefits (results will be collected after server set up)
<div align=center>
<img src='Pictures/RRT%20path%20Fix.png' width="400" height="300">
</div>

**Questions**<br>

1. Logic for collision check: use the future pose to plan grasp but use the current position for collision check.
2. Start pose collision problem: if the gripper gets touch with the target during movement, it would get stuck in next plan(they keep collided)
3. How many future steps to use to let the arm start in the next iteration (original is hard set by 0.14). This seems a meta control parameters
4. Grasp quality problem: after rank grasp the top 10 grasps might not be very good for grasp, as shown in this gif. 
<div align=center>
<img src='Pictures/Grasp%20Quality%20Problem.gif' width="400" height="300">
</div>

**Summary**<br>
1. Quickly collect results in obstacles scene
2. Start for training stage
### 02/23/2022 & 02/28/2022 Meeting5

**Update**<br>

1. Take RRT extension iterations as control parameter rather than the machine running time to fit the pipeline in different platforms (server)
2. Resolve the unstable inverse kinematics solutions problem; success rate has increased
3. Collect results for 300 trials; analyze the success rate and distribution of different time-budget; find the reason for low success rate for large time-budget is some states during one episode have no solutions, and if given large planning time, it will use them up and make target move far away.<br>
   Results Link: https://github.com/Ys-Jia/Dynamic-Grasping-Meta-Control/blob/main/Pictures/0225-motion-time.pdf
4. \[Jingxi\] About other tasks:
   - Using different vision modules to analyze the accuracy vs delay trade-off. This is hard to set up and the trade-off is not linear. Low priority.
   - Controlling prediction seems to be a better task. There are two cases:
     - Controlling how long of the past trajectories to take into consideration.
     - Controlling how long to predict into the future.

**Questions**<br>

1. Success rate is still very low; need to increase above 70%
2. Whether this task is low time-budget beneficial? When would a large time budget be better——need a more complex scene to prove!

**Summary**<br>

1. Increase the success rate of the whole pipeline first. Fix the predicted target pose bug.
2. Add some obstacles in this scene to increase benefits for large time-budget.
3. Server set-up after first 2 points completed.

### 02/16/2022 Meeting4

**Update**<br>

1. Adjust RRT planner planning pipeline to match fixed motion planning time--direct path would remember sampled nodes and record time it used.
2. Match the real motion planning consume time with the fixed motion planning time accurately.
3. Collect results for 100 trials (following baseline experiments setup) and 300 trials (random experiments setup)<br>
   Results Link: https://github.com/Ys-Jia/Dynamic-Grasping-Meta-Control/blob/main/Pictures/0216-motion-time.pdf

**Questions**<br>

1. Use iterations rather than a computer running time for environment simulation to make sure code base generalization
2. Plot the distribution of each episode to check why large time gets bad performance
3. Whether the task is biased: Fixed scene-setting for grasping task? Are results convincing--0.025 gets the best performance?
4. Next step: how to train a model for control? What module? Input/Output? Data?

**Summary**<br>

1. Complete the Questions part next week
2. Prepare to have a meeting with professor to discuss how to train a meta-controller

### 02/09/2022 Meeting3

**Update**<br>

1. Fix logistic code issues for new motion planner (Birrt) pipeline (robot arm collision, lift execution…)
2. Test performance of giving different time-budget for motion planner–the performance changes drastically (very small time-budget would make it hard for planner to find a trajectory, but give arbitrary time-budget will also make target move very far during planning and grasp failed)

Results GIF: `left:0.05 Time-budget` `right:0.14 Time-budget`

<div align=center>
<img src='Pictures/%2002-11-fixed0.05gif.gif' width="400" height="300">
<img src='Pictures/02-11-fixed0.14.gif' width="400" height="300">
</div>

Results GIF: `left:Arbitrary Time-budget` `right:Failure case`

<div align=center>
<img src='Pictures/02-11-arbitrary.gif' width="400" height="300">
<img src='Pictures/%2002-11-failuregif.gif' width="400" height="300">
</div>

**Questions**<br>

1. The actual planning time is a bit larger than time-budget set; need match it to be exact smaller than the given time-budget
2. Whether dynamic grasping task is a good task for such meta controller (the peformance would be better when time-budget given larger, or how much time-budget would affect the whole pipeline success rate?)
3. Some grasp failure cases need to fix

**Summary**

1. Collect a results table including grasping success rate by giving different fixed time-budget(linear grasp task)
2. Demonstrate the results table: why at some time-budget the arm works well, why in other setting it does not?

### 02/02/2022 Meeting2

**Update**<br>

1. Simulation environment transfers from python2 ubuntu 18.04 to python3 ubuntu 20.04 successfully. All syntax bugs have been fixed.
2. Already remove graspit and moveit! All packages build well in ROS noetic.
3. Insert Birrt motion planner and the current pipeline works well.
Sample Picture & Video:
<div align=center>
<img src='Pictures/02-03Sample.png' width="400" height="300">
<img src='Pictures/02-03GIF-2500.gif' width="400" height="300">
</div>

**Questions**<br>

1. The trajectory given by Birrt planner sometimes has collision
2. Grasp re-plan times during arm movement needs to be adjusted (too many times re-plan makes arm collide with target)
Collision:
<div align=center>
<img src='Pictures/02-03Collision.png' width="400" height="300">
</div>

**Summary**

1. Adjust the motion planner to make the whole pipeline get closed to original results (Compared with Moveit!).
2. Prune, optimize, and upload new pipeline code to github for group work.

### 01/26/2022 Meeting1

**Update**<br>

1. Setup ubuntu 20.04 environment; Find graspit could not work in 20.04 env; Seek for new package in python or ROS for grasp planning
2. Use the modified RRT planner to replace Moveit!

**Questions**<br>

1. Good grasp plan package/library in ubuntu 20.04 (ROS or pybullet; Real-time)

**Summary**

1. Jingxi thinks firstly to make sure the whole pipeline(benchmark) work well in 20.04 envrionment <br>
   Including all modules: Load Grasp -> Plan Motion -> Execute -> Collect Results

## Discribtion & Motivation:pencil: :

This project is to follow up the last semester's project-dynamic grasping and make it more intelligent. The dynamic grasping pipeline is involved with multiple submodules - grasp planner, pose estimator, motion predictor, motion planner. Each submodule has its own parameters. One of the most straightforward parameters is the time budget, and this time budget brings an important trade-off between accuracy vs delay. For example, the more time you give to the motion planner or the perception module, the better the planned trajectory or the estimated pose of the object will be. In the current pipeline, all parameters are directly set by person. However, there might not be a fixed optimal time budget throughout the whole episode. At each time step, depending on the environment, there might be a different optimal time budget for each module. Specifically, when the gripper is very far away from the target, we do not need to assign much time to the grasp-planner (the rough direction is sufficient). Also, when the gripper is very close to the target, we could reduce the time budget of the motion-planner and pose estimator so that the gripper would quickly execute the grasp based on sufficient and rough planning.

```diff
Key Words: Dynamic Grasp, Self-decided Parameters
```

**General Steps**

- [x] Replace ROS MoveIt! Planner with RRT Planner. Make sure the whole pipeline (grasp-motion-execution-results collection) works well with python 3 and Ubuntu 20.04 (Working)
- [x] Design and implement parameters-tunable module for grasp-planner, motion-planner(RRT), executer
- [ ] Train a meta controller that controls all these parameters at each time step based on the current state.
