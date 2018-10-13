clear all; close all; clc
%%
files = dir('*.par');

for f = 1:length(files)
    fid = fopen(files(f).name, 'r');
    curr_file = textscan(fid, '%f %f %f %f %s');
    block_length(f) = curr_file{1}(end)+curr_file{3}(end);
    num_NULL(f) = sum(strcmp('NULL',curr_file{5}));
end
f = figure('color', [1 1 1]);
subplot(1,2,1)
hist(block_length)
title('Block Lengths')
subplot(1,2,2)
hist(num_NULL)
title('Number of silence trials')
saveas(f, 'hists_block_silence_lengths.png', 'png')