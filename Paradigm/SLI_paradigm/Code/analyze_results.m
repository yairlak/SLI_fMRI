clear all; close all; clc

%%
subjects = 3:5;
num_subjects = length(subjects);
cnt = 0; empty_responses = 0; RTs_all_subjects = [];
for s = 1:num_subjects
    curr_subject = subjects(s);
    for run = 1:3
        file_name = sprintf('Subject_%i_run_%i.mat', curr_subject, run);
        if exist(fullfile('..', 'Output', file_name), 'file')
            cnt = cnt + 1;
            curr_data = load(fullfile('..', 'Output', file_name));
            results = curr_data.results;
            empty_responses = empty_responses + sum(results.empty_responses);
            RTs_all_subjects = [RTs_all_subjects, results.subject_responses{:,2}];
        end
    end   
end
num_trials = length(results.empty_responses);
empty_responses = 100*empty_responses/(num_trials*num_subjects*cnt);
 
f = figure('color', [1 1 1], 'visible', 'on');
hist(RTs_all_subjects,10)
xlabel('RT (sec)')
title(sprintf('RT: mean %1.2f; STD %1.2f; Missed responses %1.2f%%', mean(RTs_all_subjects), std(RTs_all_subjects), empty_responses))
file_name = sprintf('RT_hist_all_subjects.png');
saveas(f, fullfile('..','Figures', file_name), 'png')