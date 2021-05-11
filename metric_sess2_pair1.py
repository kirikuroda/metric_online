# -*- coding: utf-8 -*-

'''
fMRI metric experiment in winter, 2017
by Kiri KURODA, Dept. Social Psych, Univ. Tokyo
'''

# modules
from psychopy import core,visual,event,gui,data,misc
import pandas as pd
import numpy as np
import os,random,csv,math,itertools,pylink,glob

# magic spell...
try:
    expInfo = misc.fromFile('lastParams.pickle')
except:
    expInfo = {'Participant':'001'}
# input information
expInfo = {'id':'', 'sex':'', 'dateStr':data.getDateStr(format='%Y%m%d%H%M')}
dlg = gui.DlgFromDict(dictionary=expInfo, order=['id', 'sex'], title='fMRI Experiment', fixed=['dateStr'])
# magic spell...
if dlg.OK:
    misc.toFile('lastParams.pickle', expInfo)
else:
    core.quit()
# check typo
if expInfo['id'] == '' or (expInfo['sex'] != 'm' and expInfo['sex'] != 'f'):
    print('Typo! Please be careful...')
    core.quit()
# define quit-function
def quit_exp():
    if event.getKeys(keyList=['escape']):
        behavior_file.close()
        log_file.close()
        if eyeflg:
            tracker.stopRecording()
            tracker.setOfflineMode()
            tracker.closeDataFile()
            #tracker.receiveDataFile(edf_file_name, edf_file_name)
            tracker.close()
        core.quit()

# set a data file
try:
    os.makedirs('./data/behavior/pair1')
except OSError:
    pass
try:
    os.makedirs('./data/log/pair1')
except OSError:
    pass
cwd = os.getcwd()
behavior_file = open(os.path.join(cwd+'/data/behavior/pair1/metric_mri_pair1_behavior_'+expInfo['id']+'_'+expInfo['dateStr']+'.csv'), 'wb')
log_file = open(os.path.join(cwd+'/data/log/pair1/metric_mri_pair1_log_'+expInfo['id']+'_'+expInfo['dateStr']+'.csv'), 'wb')
behavior_csv = csv.writer(behavior_file)
log_csv = csv.writer(log_file)
behavior_csv.writerow(['cond', 'session', 'id', 'sex', 'trial', 'num', 'pattern', 'estimation', 'response', 'rt', 'pair_weight', 'pair_num'])
log_csv.writerow(['fMRI metric experiment at Univ Tokyo'])
log_csv.writerow(['Logfile written in ' + expInfo['dateStr']])
log_csv.writerow([''])
log_csv.writerow(['cond', 'session', 'id', 'sex', 'trial', 'event', 'time', 'duration', 'num', 'pattern', 'estimation', 'digit', 'pair_num'])

'''
parameters
'''

session = 2

# participant's information
id = int(expInfo['id'])
if expInfo['sex'] == 'm':
    sex = 'male'
else:
    sex = 'female'

if id % 4 == 1 or id % 4 == 2:
    cond = 'convergent'
else:
    cond = 'indifferent'

initial_weight = 0.609441 # mean - 1.5 SD
a1 = 0.091
a2 = 0.044
a3 = 0.037
a4 = 0.032
a5 = 0.025
b1 = 0.066
b2 = 0.014
b3 = 0.001
b4 = -0.015
b5 = -0.011
pars_other = np.array([a1, a2, a3, a4, a5])
pars_self = np.array([b1, b2, b3, b4, b5])
weights_other = np.array([initial_weight, 0, 0, 0, 0])
weights_self = np.zeros(5)

# set a window (refresh rate = 60fps)
win = visual.Window(size=(1920,1080), allowGUI=False, units='pix', color=(-1,-1,-1), fullscr=True)
width, height = win.size

# stimuli and trial
stimuli_data = pd.read_csv('metric_mri_stimuli.csv')
num_trial = 48
num_level = 12
num_min = 25
num_max = 58
gap = 3
pattern_list = np.random.permutation(range(100))
num_list = list(itertools.chain.from_iterable([np.random.permutation(range(num_min, num_max + 1, gap)) for i in range(num_trial/num_level)]))
isi_list = np.random.permutation(list(itertools.chain.from_iterable([[2]*(num_trial/3), [3]*(num_trial/3), [4]*(num_trial/3)])))
iti_list = np.random.permutation(list(itertools.chain.from_iterable([[2]*(num_trial/3), [3]*(num_trial/3), [4]*(num_trial/3)])))

text_size = 120
fixation = visual.TextStim(win, text='+', color=(1,1,1), height=80)
presentation = 0.8 # seconds
timeout = 6.2
feedback = 2
dodge = text_size * 0.6 # dodge text
square_tens_place = visual.Rect(win, width=text_size, height=text_size, pos=(-dodge, 0))
square_ones_place = visual.Rect(win, width=text_size, height=text_size, pos=(dodge, 0))

instruction = visual.TextStim(win, text=u'ドットの個数を答えてください。\n※Aさんと同時に取り組むブロックです。', height=60, font='Meiryo')

you_text = visual.TextStim(win, text=u'あなた', height=80, font='Meiryo', pos=(-480, 270))
partner_text = visual.TextStim(win, text=u'Aさん', height=80, font='Meiryo', pos=(480, 270))

'''
eyetracker
'''
edf_file_name = 'sess2_' + str(id) + '.edf'
print('Connecting to the eyetracker...')
clock = core.Clock()
try:
    tracker = pylink.EyeLink()
except RuntimeError:
    print('Connection: Failed')
    eyeflg = False
else:
    print('Connection: Success')
    eyeflg = True
    time_correction = clock.getTime() - tracker.trackerTime()
    tracker.openDataFile(edf_file_name)
    
    eyelink_ver = tracker.getTrackerVersion()
    
    tracker.sendCommand('saccade_velocity_threshold = 30')
    tracker.sendCommand('saccade_acceleration_threshold = 9500')

if eyeflg:
    tracker.startRecording(1,1,1,1)

'''
experiment
'''

# wait for the trigger
instruction.draw()
win.flip()
onset = core.Clock()
prepare = 'yet'
while 1:
    quit_exp()
    if prepare == 'yet':
        stimuli_set = stimuli_data[(stimuli_data.num == num_list[0]) & (stimuli_data.pattern == pattern_list[0])]
        dot = [stimuli_set[stimuli_set.id == j] for j in range(int(num_list[0]))]
        dots = [visual.Circle(win, radius=int(dot[j]["radius"]), fillColor=(float((dot[j]["red"]/255)*2-1), float((dot[j]["green"]/255)*2-1), float((dot[j]["blue"]/255)*2-1)), lineColor=(float((dot[j]["red"]/255)*2-1), float((dot[j]["green"]/255)*2-1), float((dot[j]["blue"]/255)*2-1)), pos=(int(dot[j]["x"]), int(dot[j]["y"]))) for j in range(int(num_list[0]))]
        map(visual.Circle.draw, dots)
        prepare = 'done'
    if event.getKeys(keyList=['t']):
        onset_exp = core.Clock()
        time = -onset.getTime()
        duration = -time
        log_csv.writerow([cond, session, id, sex, 'NA', 'instruction', time, duration, 'NA', 'NA', 'NA', 'NA', 'NA'])
        break
prepare = 'yet'

# start the experiment
for i in range(num_trial):
    
    # stimuli presentation
    if eyeflg:
        tracker.sendMessage('trial' + str(i+1))
    fixation.draw()
    win.flip()
    onset = core.Clock()
    time = onset_exp.getTime()
    while onset.getTime() < presentation:
        pass
    duration = onset.getTime()
    log_csv.writerow([cond, session, id, sex, i+1, 'cue', time, duration, num_list[i], pattern_list[i], 'NA', 'NA', 'NA'])
    
    # ISI(2000, 4000, or 6000ms)
    fixation.draw()
    win.flip()
    onset = core.Clock()
    time = onset_exp.getTime()
    prepare = 'yet'
    while onset.getTime() < isi_list[i]:
        # calculate partner's weight parameter during ISI
        if cond == 'convergent':
            while prepare == 'yet':
                if i == 0:
                    w = weights_other[0]
                elif i == 1:
                    w = initial_weight + weights_other[0] * pars_other[0] + weights_self[0] * pars_self[0]
                elif i == 2:
                    w = initial_weight + sum(weights_other[0:2] * pars_other[0:2]) + sum(weights_self[0:2] * pars_self[0:2])
                elif i == 3:
                    w = initial_weight + sum(weights_other[0:3] * pars_other[0:3]) + sum(weights_self[0:3] * pars_self[0:3])
                elif i == 4:
                    w = initial_weight + sum(weights_other[0:4] * pars_other[0:4]) + sum(weights_self[0:4] * pars_self[0:4])
                else:
                    w = initial_weight + sum(weights_other * pars_other) + sum(weights_self * pars_self)
                if w > 0:
                    weight_other = w
                    weights_other[4] = weights_other[3]
                    weights_other[3] = weights_other[2]
                    weights_other[2] = weights_other[1]
                    weights_other[1] = weights_other[0]
                    weights_other[0] = weight_other
                    prepare = 'done'
                    break
        else: # indifferent
            weight_other = initial_weight
    
    duration = onset.getTime()
    log_csv.writerow([cond, session, id, sex, i+1, 'isi', time, duration, num_list[i], pattern_list[i], 'NA', 'NA', 'NA'])
    
    # estimation (require response)
    tens_place = 0
    ones_place = 0
    text_tens_place = visual.TextStim(win, text=str(tens_place), height=text_size, pos=(-dodge,0), font='Meiryo')
    text_ones_place = visual.TextStim(win, text=str(ones_place), height=text_size, pos=(dodge,0), font='Meiryo')
    text_tens_place.draw()
    text_ones_place.draw()
    square_tens_place.draw()
    response = 'tens'
    win.flip()
    onset = core.Clock()
    time = onset_exp.getTime()
    rt = timeout
    quit_exp()
    event.clearEvents()
    log_csv.writerow([cond, session, id, sex, i+1, 'onset_estimation', time, 'NA', num_list[i], pattern_list[i], 'NA', response, 'NA'])
    while onset.getTime() < timeout:
        if response == 'tens':
            if event.getKeys(keyList=['b']):
                tens_place = (tens_place + 1) % 10
                text_tens_place = visual.TextStim(win, text=str(tens_place), height=text_size, pos=(-dodge,0), font='Meiryo')
                text_tens_place.draw()
                text_ones_place.draw()
                square_tens_place.draw()
                time = onset_exp.getTime()
                log_csv.writerow([cond, session, id, sex, i+1, 'up_tens', time, 'NA', num_list[i], pattern_list[i], 'NA', response, 'NA'])
                win.flip()
            elif event.getKeys(keyList=['y']):
                response = 'ones'
                text_tens_place.draw()
                text_ones_place.draw()
                square_ones_place.draw()
                time = onset_exp.getTime()
                log_csv.writerow([cond, session, id, sex, i+1, 'change_digit_to_ones', time, 'NA', num_list[i], pattern_list[i], 'NA', response, 'NA'])
                win.flip()
        elif response == 'ones':
            if event.getKeys(keyList=['b']):
                ones_place = (ones_place + 1) % 10
                text_ones_place = visual.TextStim(win, text=str(ones_place), height=text_size, pos=(dodge,0), font='Meiryo')
                text_tens_place.draw()
                text_ones_place.draw()
                square_ones_place.draw()
                time = onset_exp.getTime()
                log_csv.writerow([cond, session, id, sex, i+1, 'up_ones', time, 'NA', num_list[i], pattern_list[i], 'NA', response, 'NA'])
                win.flip()
            elif event.getKeys(keyList=['y']):
                response = 'tens'
                text_tens_place.draw()
                text_ones_place.draw()
                square_tens_place.draw()
                time = onset_exp.getTime()
                log_csv.writerow([cond, session, id, sex, i+1, 'change_digit_to_tens', time, 'NA', num_list[i], pattern_list[i], 'NA', response, 'NA'])
                win.flip()
        # decision
        if event.getKeys(keyList=['g']):
            rt = onset.getTime()
            response = 'done'
            time = onset_exp.getTime()
            estimation = tens_place * 10 + ones_place
            log_csv.writerow([cond, session, id, sex, i+1, 'decision', time, 'NA', num_list[i], pattern_list[i], estimation, response, 'NA'])
            fixation.draw()
            win.flip()
    estimation = tens_place * 10 + ones_place
    
    # feedback (2000ms)
    other_estimation = int(round(num_list[i] * weight_other + random.randint(-1,1)))
    you_num_text = visual.TextStim(win, text=str(estimation), pos=(-480, 0), height=80, font='Meiryo')
    partner_num_text = visual.TextStim(win, text=str(other_estimation), pos=(480, 0), height=80, font='Meiryo')
    you_text.draw()
    partner_text.draw()
    you_num_text.draw()
    partner_num_text.draw()
    win.flip()
    onset = core.Clock()
    time = onset_exp.getTime()
    while onset.getTime() < feedback:
        pass
    duration = onset.getTime()
    log_csv.writerow([cond, session, id, sex, i+1, 'feedback', time, duration, num_list[i], pattern_list[i], 'NA', 'NA', other_estimation])
    
    # ITI (2000, 4000, or 6000ms)
    fixation.draw()
    win.flip()
    onset = core.Clock()
    time = onset_exp.getTime()
    prepare = 'yet'
    if eyeflg:
        tracker.stopRecording()
        tracker.startRecording(1,1,1,1)
    while onset.getTime() < iti_list[i] - 0.5:
        if i != num_trial - 1:
            if prepare == 'yet':
                stimuli_set = stimuli_data[(stimuli_data.num == num_list[i+1]) & (stimuli_data.pattern == pattern_list[i+1])]
                dot = [stimuli_set[stimuli_set.id == j] for j in range(int(num_list[i+1]))]
                dots = [visual.Circle(win, radius=int(dot[j]["radius"]), fillColor=(float((dot[j]["red"]/255)*2-1), float((dot[j]["green"]/255)*2-1), float((dot[j]["blue"]/255)*2-1)), lineColor=(float((dot[j]["red"]/255)*2-1), float((dot[j]["green"]/255)*2-1), float((dot[j]["blue"]/255)*2-1)), pos=(int(dot[j]["x"]), int(dot[j]["y"]))) for j in range(int(num_list[i+1]))]
                map(visual.Circle.draw, dots)
                prepare = 'done'
    prepare = 'yet'
    behavior_csv.writerow([cond, session, id, sex, i+1, num_list[i], pattern_list[i], estimation, response, rt, weight_other, other_estimation])
    weight_self = float(estimation)/float(num_list[i])
    weights_self[4] = weights_self[3]
    weights_self[3] = weights_self[2]
    weights_self[2] = weights_self[1]
    weights_self[1] = weights_self[0]
    weights_self[0] = weight_self
    
    # wait fot the trigger
    event.clearEvents()
    while 1:
        if event.getKeys(keyList=['t']):
            duration = onset.getTime()
            log_csv.writerow([cond, session, id, sex, i+1, 'iti', time, duration, num_list[i], pattern_list[i], 'NA', 'NA', 'NA'])
            break
    quit_exp()

# margin
onset = core.Clock()
time = onset_exp.getTime()
while onset.getTime() < 8:
    pass
duration = onset.getTime()
log_csv.writerow(['NA', session, id, sex, 'NA', 'margin', time, duration, 'NA', 'NA', 'NA', 'NA', 'NA'])


# stop the eyetracker
if eyeflg:
    tracker.stopRecording()
    tracker.setOfflineMode()
    tracker.closeDataFile()
    #tracker.receiveDataFile(edf_file_name, edf_file_name)
    tracker.close()

# finish the experiment
win.close()
core.quit()