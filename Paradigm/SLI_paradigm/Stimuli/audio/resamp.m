clear all; close all; clc
%%
files = dir('*.wav');

for f = 1:length(files)
    curr_file = files(f).name;
    [y, fs] = audioread(curr_file);
    y_new = resample(y, 44100, fs);
    y_new = y_new / max(y_new);
    audiowrite(curr_file, y_new, 44100)
end