import pickle

label_num2str={}

event_dict={
    'VT':'Vault', # 跳马
    'FX':'Floor Exercise',
    'BB':'Balance Beam', # 平衡杠
    'UB':'Uneven Bars' # 高低杠
}

action_dict = {
    '1':'vault',
    '21':'FX_leap_jump_hop',
    '22':'FX_turns',
    '23':'FX_side_salto',
    '24':'FX_front_salto',
    '25':'FX_back_salto',
    '31':'BB_leap_jump_hop',
    '32':'BB_turns',
    '33':'BB_flight_salto',
    '34':'BB_flight_handspring',
    '35':'BB_dismounts',
    '41':'UB_circles',
    '42':'UB_fligh_same_bar',
    '43':'UB_transition_flight',
    '44':'UB_dismounts'
}

# location of gym288_categories.txt
folder="dataset_info/finegym/categories/gym288_categories.txt"
with open(folder, mode='r') as f:
    lines = f.readlines()
    for line in lines:
        # print(line)
        l=line.split(";")
        idx=l[-1].index(")")
        num_label=l[0].split(" ")[-1]
        event_label=event_dict[l[-1][2:4]]
        action_label=action_dict[l[1].split(" ")[-1]]
        stage_label=l[-1][idx+1:]
        # print(num_label,event_label,action_label,stage_label)
        label_num2str[num_label]=f'{event_label}->{action_label}->{stage_label}'
f.close()

with open('label_num2str.pkl', 'wb') as f:
    pickle.dump(label_num2str, f)