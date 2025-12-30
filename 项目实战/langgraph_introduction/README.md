# 这是Langgraph实战入门

1. [graph_put_elephant](graph_put_elephant.py)
> 这是一个通过简单流程让你熟悉langgraph搭建工作流的示例。
  <br> **把大象放入冰箱**
  <br> 1. 打开冰箱门      (open_fridge)
  <br> 2. 把大象放进冰箱  (put_elephant)
  <br> 3. 关闭冰箱门     (close_fridge)

2. [graph_human_put_elephant](graph_human_put_elephant.py)
> 同样是把大象放入冰箱，但是这次我们添加对大象尺寸的过滤
<br> 1. 打开冰箱门
<br> 2. 判断大象尺寸
<br> 2.1 如果大象尺寸小于3，大象完全可以放入冰箱，直接放入冰箱，跳转到关闭冰箱门
<br> 2.2 如果大象尺寸大于8，大象尺寸过大，冰箱放不下，大象不放进冰箱，关闭冰箱门
<br> 2.3 如果大象尺寸介于两者之间，由人工参与决定放不放进冰箱，关闭冰箱门

3. 
> 