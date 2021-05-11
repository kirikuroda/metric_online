# -*- coding: utf-8 -*-

'''
fMRI metric experiment in winter, 2017
by Kiri KURODA, Dept. Social Psych, Univ. Tokyo
'''

# modules
from psychopy import core,visual,event,gui,data,misc
import pandas as pd
import numpy as np
import os,random,csv,math,itertools,pylink

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
    os.makedirs('./data/behavior/practice')
except OSError:
    pass
try:
    os.makedirs('./data/log/practice')
except OSError:
    pass
cwd = os.getcwd()
behavior_file = open(os.path.join(cwd+'/data/behavior/practice/metric_mri_behavior_practice_'+expInfo['id']+'_'+expInfo['dateStr']+'.csv'), 'wb')
log_file = open(os.path.join(cwd+'/data/log/practice/metric_mri_log_practice_'+expInfo['id']+'_'+expInfo['dateStr']+'.csv'), 'wb')
behavior_csv = csv.writer(behavior_file)
log_csv = csv.writer(log_file)
behavior_csv.writerow(['cond', 'session', 'id', 'sex', 'trial', 'num', 'pattern', 'estimation', 'response', 'rt'])
log_csv.writerow(['fMRI metric experiment at Univ Tokyo'])
log_csv.writerow(['Logfile written in ' + expInfo['dateStr']])
log_csv.writerow([''])
log_csv.writerow(['cond', 'session', 'id', 'sex', 'trial', 'event', 'time', 'duration', 'num', 'pattern', 'estimation', 'digit'])

'''
parameters
'''

session = 0

# set a window (refresh rate = 60fps)
win = visual.Window(size=(1920,1080), fullscr=True, allowGUI=False, units='pix', color=(-1,-1,-1))
width, height = win.size

# participant's information
id = int(expInfo['id'])
if expInfo['sex'] == 'm':
    sex = 'male'
else:
    sex = 'female'

# stimuli and trial
stimuli_data = pd.read_csv('metric_mri_stimuli.csv')
num_trial = 24
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
dodge = text_size * 0.6 # dodge text
square_tens_place = visual.Rect(win, width=text_size, height=text_size, pos=(-dodge, 0))
square_ones_place = visual.Rect(win, width=text_size, height=text_size, pos=(dodge, 0))

num_text = visual.TextStim(win, text=u'個数を答えてください。', height=60, font='Meiryo')
color_text = visual.TextStim(win, text=u'色温度を答えてください。', height=60, font='Meiryo')
miss_text = visual.TextStim(win, text=u'Miss!', height=60, font='Meiryo')

'''
eyetracker
'''
edf_file_name = 'sess0_' + str(id) + '.edf'
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
if id % 8 >= 1 and id % 8 <= 4:
    cond = 'practice_num'
    num_text.draw()
else:
    cond = 'practice_color'
    color_text.draw()
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
        log_csv.writerow([cond, session, id, sex, 'NA', 'instruction', time, duration, 'NA', 'NA', 'NA', 'NA'])
        break
prepare = 'yet'

# start the experiment
for i in range(num_trial):
    
    # change instruction
    if i == 12:
        if id % 8 >= 1 and id % 8 <= 4:
            cond = 'practice_color'
            color_text.draw()
        else:
            cond = 'practice_num'
            num_text.draw()
        win.flip()
        onset = core.Clock()
        time = onset_exp.getTime()
        prepare = 'yet'
        while onset.getTime() < 4:
            if prepare == 'yet':
                stimuli_set = stimuli_data[(stimuli_data.num == num_list[i]) & (stimuli_data.pattern == pattern_list[i])]
                dot = [stimuli_set[stimuli_set.id == j] for j in range(int(num_list[i]))]
                dots = [visual.Circle(win, radius=int(dot[j]["radius"]), fillColor=(float((dot[j]["red"]/255)*2-1), float((dot[j]["green"]/255)*2-1), float((dot[j]["blue"]/255)*2-1)), lineColor=(float((dot[j]["red"]/255)*2-1), float((dot[j]["green"]/255)*2-1), float((dot[j]["blue"]/255)*2-1)), pos=(int(dot[j]["x"]), int(dot[j]["y"]))) for j in range(int(num_list[i]))]
                map(visual.Circle.draw, dots)
                prepare = 'done'
        prepare = 'yet'
        duration = onset.getTime()
        log_csv.writerow([cond, session, id, sex, i+1, 'instruction', time, duration, 'NA', 'NA', 'NA', 'NA'])
    
    # stimuli presentation
    if eyeflg:
        tracker.sendMessage('trial' + str(i + 1))
    fixation.draw()
    win.flip()
    onset = core.Clock()
    time = onset_exp.getTime()
    while onset.getTime() < presentation:
        pass
    duration = onset.getTime()
    log_csv.writerow([cond, session, id, sex, i+1, 'cue', time, duration, num_list[i], pattern_list[i], 'NA', 'NA'])
    
    # ISI(2000, 4000, or 6000ms)
    fixation.draw()
    win.flip()
    onset = core.Clock()
    time = onset_exp.getTime()
    while onset.getTime() < isi_list[i]:
        pass
    duration = onset.getTime()
    log_csv.writerow([cond, session, id, sex, i+1, 'isi', time, duration, num_list[i], pattern_list[i], 'NA', 'NA'])
    
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
    log_csv.writerow([cond, session, id, sex, i+1, 'onset_estimation', time, 'NA', num_list[i], pattern_list[i], 'NA', response])
    while onset.getTime() < timeout:
        if response == 'tens':
            if event.getKeys(keyList=['b']):
                tens_place = (tens_place + 1) % 10
                text_tens_place = visual.TextStim(win, text=str(tens_place), height=text_size, pos=(-dodge,0), font='Meiryo')
                text_tens_place.draw()
                text_ones_place.draw()
                square_tens_place.draw()
                time = onset_exp.getTime()
                log_csv.writerow([cond, session, id, sex, i+1, 'up_tens', time, 'NA', num_list[i], pattern_list[i], 'NA', response])
                win.flip()
            elif event.getKeys(keyList=['y']):
                response = 'ones'
                text_tens_place.draw()
                text_ones_place.draw()
                square_ones_place.draw()
                time = onset_exp.getTime()
                log_csv.writerow([cond, session, id, sex, i+1, 'change_digit_to_ones', time, 'NA', num_list[i], pattern_list[i], 'NA', response])
                win.flip()
        elif response == 'ones':
            if event.getKeys(keyList=['b']):
                ones_place = (ones_place + 1) % 10
                text_ones_place = visual.TextStim(win, text=str(ones_place), height=text_size, pos=(dodge,0), font='Meiryo')
                text_tens_place.draw()
                text_ones_place.draw()
                square_ones_place.draw()
                time = onset_exp.getTime()
                log_csv.writerow([cond, session, id, sex, i+1, 'up_ones', time, 'NA', num_list[i], pattern_list[i], 'NA', response])
                win.flip()
            elif event.getKeys(keyList=['y']):
                response = 'tens'
                text_tens_place.draw()
                text_ones_place.draw()
                square_tens_place.draw()
                time = onset_exp.getTime()
                log_csv.writerow([cond, session, id, sex, i+1, 'change_digit_to_tens', time, 'NA', num_list[i], pattern_list[i], 'NA', response])
                win.flip()
        # decision
        if event.getKeys(keyList=['g']):
            rt = onset.getTime()
            response = 'done'
            time = onset_exp.getTime()
            estimation = tens_place * 10 + ones_place
            log_csv.writerow([cond, session, id, sex, i+1, 'decision', time, 'NA', num_list[i], pattern_list[i], estimation, response])
            fixation.draw()
            win.flip()
    estimation = tens_place * 10 + ones_place
    
    if response != 'done':
        miss_text.draw()
        win.flip()
        onset = core.Clock()
        time = onset_exp.getTime()
        while onset.getTime() < 1.5:
            pass
        duration = onset.getTime()
        log_csv.writerow([cond, session, id, sex, i+1, 'miss', time, duration, num_list[i], pattern_list[i], 'NA', 'NA'])
    
    # ITI (2000, 4000, or 6000ms)
    fixation.draw()
    win.flip()
    onset = core.Clock()
    time = onset_exp.getTime()
    prepare = 'yet'
    if eyeflg:
        tracker.stopRecording()
        tracker.startRecording(1,1,1,1)
    while onset.getTime() < iti_list[i]:
        if i != 11 and i != 23:
            if prepare == 'yet':
                stimuli_set = stimuli_data[(stimuli_data.num == num_list[i+1]) & (stimuli_data.pattern == pattern_list[i+1])]
                dot = [stimuli_set[stimuli_set.id == j] for j in range(int(num_list[i+1]))]
                dots = [visual.Circle(win, radius=int(dot[j]["radius"]), fillColor=(float((dot[j]["red"]/255)*2-1), float((dot[j]["green"]/255)*2-1), float((dot[j]["blue"]/255)*2-1)), lineColor=(float((dot[j]["red"]/255)*2-1), float((dot[j]["green"]/255)*2-1), float((dot[j]["blue"]/255)*2-1)), pos=(int(dot[j]["x"]), int(dot[j]["y"]))) for j in range(int(num_list[i+1]))]
                map(visual.Circle.draw, dots)
                prepare = 'done'
    duration = onset.getTime()
    prepare = 'yet'
    behavior_csv.writerow([cond, session, id, sex, i+1, num_list[i], pattern_list[i], estimation, response, rt])
    log_csv.writerow([cond, session, id, sex, i+1, 'iti', time, duration, num_list[i], pattern_list[i], 'NA', 'NA'])
    
    """
    # wait fot the trigger
    event.clearEvents()
    while 1:
        if event.getKeys(keyList=['t']):
            duration = onset.getTime()
            log_csv.writerow([cond, session, id, sex, i+1, 'iti', time, duration, num_list[i], pattern_list[i], 'NA', 'NA'])
            break
    """
    
    quit_exp()

# margin
onset = core.Clock()
time = onset_exp.getTime()
while onset.getTime() < 8:
    pass
duration = 8
log_csv.writerow(['NA', session, id, sex, 'NA', 'margin', time, duration, 'NA', 'NA', 'NA', 'NA'])


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