clear all; close all; clc

addpath('functions')
% Add_Psych
% cd('C:\toolbox\Psychtoolbox')
% SetupPsychtoolbox
% cd('C:\Users\LENOVO\Documents\MATLAB\SLI fMRI Experiment\Paradigm\SLI_paradigm\Code')

% PsychPortAudio3('Close');
%% CHANGE BEFORE RUN
answer = inputdlg({'Subject name', 'Run number (1-3)'}, 'Input', 1);
subject = str2double(answer{1});
run = str2double(answer{2});
rng(subject) % Set the random number generator seed according to subject #
filename = sprintf('Subject_%i_run_%i.mat', subject, run);
A = exist(fullfile('..', 'Output', filename), 'file');
if A == 2
    msgbox(sprintf('File already exists : %s\nPlease change subject number or run', filename));
    error('Please change subject number or run')
end
params = load_params(run);

%% Run paradigm
results = main_SLI(subject, run, params);
results.empty_responses = cellfun(@isempty, results.subject_responses(:,1));
results.percentage_empty_responses = round(100*sum(results.empty_responses)/length(results.subject_responses));
results.output_filename = fullfile('..', 'Output', filename);

%% Save results
save(fullfile('..', 'Output', filename), 'results')
fprintf('Results saved into %s\n', results.output_filename);
fclose('all')

%% Genereate figures (RT histogram) and save to Figures folder
if size(results.subject_responses,2)>1       
    f = figure('color', [1 1 1], 'visible', 'off');
    hist([results.subject_responses{:,2}])
    xlabel('RT (sec)')
    title(['Mean response time ' num2str(mean([results.subject_responses{:,2}]))])
    file_name = sprintf('RT_hist_subject_%i_run_%i.png', subject, run);
    saveas(f, fullfile('..','Figures', file_name), 'png')
end