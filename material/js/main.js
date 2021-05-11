/*
@file Follow-up Online Experiments
@author Kiri Kuroda <kuroda.kiri@gmail.com>
*/

"use strict";

//////////////////////
// Initial settings //
// 初期設定         //
//////////////////////

// Set the participant's id and a random seed
// 参加者固有のIDを振る。乱数のシードを設定する
const subj_id = jsPsych.randomization.randomID();
Math.seedrandom(subj_id);

// Assignment to the condition
// 条件割当
const assignment = jsPsych.randomization.sampleWithoutReplacement([0,1,2,3], 1);

// Asch or Sherif
let agent_type = "agent";
if (assignment % 2 === 0) {
  agent_type = "asch";
} else {
  agent_type = "sherif";
}

// Underestimation or overestimation
let estim_bias = "bias";
if (Math.floor(assignment / 2) === 0) {
  estim_bias = "underestimation";
} else {
  estim_bias = "overestimation"
}

// Record the date
// 日付を記録する
const today = new Date();
const year = today.getFullYear();
const month = `0${today.getMonth() + 1}`.slice(-2);
const date = `0${today.getDate()}`.slice(-2);
const hour = `0${today.getHours()}`.slice(-2);
const minute = `0${today.getMinutes()}`.slice(-2);
const second = `0${today.getSeconds()}`.slice(-2);
const recording_date = `${year}${month}${date}${hour}${minute}${second}_${subj_id}`;

// Add the ID and condition to all trials
// 全試行にIDと条件名を付与する
jsPsych.data.addProperties({subj_id: subj_id, agent_type: agent_type, estim_bias: estim_bias});

// Number of dots
// ドットの数
const arr_num_dots = Array.apply(null, new Array(12)).map(function(v, i){return 25 + (i * 3);});

// Number of trials
// 試行数
const trial_num_practice = arr_num_dots.length * 2;
const trial_num_preinteraction = arr_num_dots.length * 2;
const trial_num_interaction = arr_num_dots.length * 4;
const trial_num_postinteraction = arr_num_dots.length * 2;

// Make each parameter's list
// 各パラメタのリストを作る

// Practice
let num_dots_practice = [];
for (let i = 0; i < (trial_num_practice / arr_num_dots.length); i++) {
  num_dots_practice.push(jsPsych.randomization.shuffle(arr_num_dots));
}
num_dots_practice = num_dots_practice.reduce((pre, current) => {pre.push(...current); return pre}, []);

// Preinteraction
let num_dots_preinteraction = [];
for (let i = 0; i < (trial_num_preinteraction / arr_num_dots.length); i++) {
  num_dots_preinteraction.push(jsPsych.randomization.shuffle(arr_num_dots));
}
num_dots_preinteraction = num_dots_preinteraction.reduce((pre, current) => {pre.push(...current); return pre}, []);

// Interaction
let num_dots_interaction = [];
for (let i = 0; i < (trial_num_interaction / arr_num_dots.length); i++) {
  num_dots_interaction.push(jsPsych.randomization.shuffle(arr_num_dots));
}
num_dots_interaction = num_dots_interaction.reduce((pre, current) => {pre.push(...current); return pre}, []);

// Postinteraction
let num_dots_postinteraction = [];
for (let i = 0; i < (trial_num_postinteraction / arr_num_dots.length); i++) {
  num_dots_postinteraction.push(jsPsych.randomization.shuffle(arr_num_dots));
}
num_dots_postinteraction = num_dots_postinteraction.reduce((pre, current) => {pre.push(...current); return pre}, []);

// All phases
const num_dots_all = num_dots_practice.concat(num_dots_preinteraction, num_dots_interaction, num_dots_postinteraction);
const id_dots_all = Array(num_dots_all.length);
for (let num of arr_num_dots) {
  let stim_ids = jsPsych.randomization.shuffle([0,1,2,3,4,5,6,7,8,9]);
  let num_index = [];
  for (let i = 0; i < num_dots_all.length; i++) {
    if (num_dots_all[i] === num) {
      num_index.push(i);
    }
  }
  for (let i = 0; i < num_index.length; i++) {
    id_dots_all[num_index[i]] = stim_ids[i];
  }
}

// Define the HTML elements
// テキスト刺激（HTML要素）をカウンターバランスに応じて定義する
const trial_param_practice = {
  num_dots: num_dots_all.slice[0, 24],
  id_dots: id_dots_all.slice[0, 24]
}
const trial_param_preinteraction = {
  num_dots: num_dots_all.slice[24, 48],
  id_dots: id_dots_all.slice[24, 48]
}
const trial_param_interaction = {
  num_dots: num_dots_all.slice[48, 96],
  id_dots: id_dots_all.slice[48, 96]
}
const trial_param_postinteraction = {
  num_dots: num_dots_all.slice[96, 120],
  id_dots: id_dots_all.slice[96, 120]
}


/////////////////////////////
// Create trial components //
// 1試行の部品を作る       //
/////////////////////////////

// Start the task
// メインブロック開始
const start_task = {
  type: "html-keyboard-response",
  stimulus: `
    <p>
      スペースキーを押すと、すぐに本番が始まります。<br>
      よろしくお願いいたします。
    </p>
  `,
  choices: ["space"],
  data: {block: "start_task"}
};

// (i) Fixation cross
// (i) 注視点
const fixation = {
  type: "html-keyboard-response",
  choices: jsPsych.NO_KEYS,
  stimulus: `<div class="fixation">+</div>`,
  trial_duration: function() {
    return jsPsych.randomization.sampleWithoutReplacement([1000, 2000, 3000], 1)[0];
  },
  data: {part: "fixation"},
  save_trial_parameters: {
    trial_duration: true
  }
};
const data_dots = {};
$.ajax({
  url: "csvjson.json",
  dataType: "json",
  async: false
  })
  .done(function(data) {
    data_dots = data;
  })
  .fail(function() {
    console.log("ajax failed...");
  });


// (ii) Stimulus presentation
// (ii) 刺激呈示
const present_stimuli = {
  type: "canvas-keyboard-response",
  stimulus: "a",
  // stimulus: function drawCircle(c) {
  //   let xs = ;
  //   let ctx = c.getContext("2d");
  //   for (let i = 0; i < jsPsych.timelineVariable("num_dots"); i++) {
  //     ctx.beginPath();
  //     let x = jsPsych.timelineVariable("num_dots");
  //   }
  // },
  choices: jsPsych.NO_KEYS,
  trial_duration: 800,
  data: {

  }
}



jsPsych.init({
  timeline: [],
  override_safe_mode: true
});
