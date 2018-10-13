function stimuli = load_stimuli(win, subject, run, params)
% This function loads images and audio files into a struct of stimuli

%% Paths
path2stimuli_visual = fullfile('..', 'Stimuli', 'visual');
path2stimuli_audio = fullfile('..', 'Stimuli', 'audio');

%% Load file names of both visual and audio stimuli are from text files
list_number = (subject-1)*3 + run;
[optseq_list.timing, optseq_list.condition_number, optseq_list.stimulus_duration, ~, optseq_list.condition_name] = textread(fullfile('..', 'Stimuli', 'token lists from optseq', sprintf('SLI-%03i.par', list_number)), '%f\t%d\t%f\t%f\t%s');
stimuli.num_trials = length(optseq_list.condition_number); % Trials including NULL conditions
% token_order_in_curr_block = randperm(params.num_trials); % Trials *NOT* including NULL conditions

%% Build stimuli struct for output
cnt.ZM = 0; cnt.SZVO = 0; cnt.SVOZ = 0; cnt.OVS = 0; cnt.MIDDLE = 0;
token_number_cnt = 0; % Omit NULL conditions from counting
cnt_FIL = 0; % Count the filler number to decide MIDDLE/OVS
for i = 1:stimuli.num_trials
    stimuli.condition_name{i} = optseq_list.condition_name{i};
    if ~strcmp(optseq_list.condition_name{i}, 'NULL')
        token_number_cnt = token_number_cnt + 1;
%         curr_token_number = token_order_in_curr_block(token_number_cnt);
        switch optseq_list.condition_name{i}          
            case 'FIL'
                cnt_FIL = cnt_FIL + 1;
                if ismember(cnt_FIL, params.MIDDLE_filler_positions)
                    curr_condition_name = 'MIDDLE';
                else
                    curr_condition_name = 'OVS';
                end

            otherwise
                curr_condition_name = optseq_list.condition_name{i};
        end
        cnt.(curr_condition_name) = cnt.(curr_condition_name) + 1;
        curr_cnd_token_number = params.stim_numbers.(curr_condition_name)(cnt.(curr_condition_name));
        % load AUDITORY
        stimuli.auditory(i).auditori_file_name = sprintf('%s%i.wav', curr_condition_name, curr_cnd_token_number);
        stimuli.auditory(i).file_name = fullfile(path2stimuli_audio, stimuli.auditory(i).auditori_file_name);
        [stimuli.auditory(i).y, stimuli.auditory(i).fs] = audioread(stimuli.auditory(i).file_name);
        stimuli.auditory(i).y = stimuli.auditory(i).y(:,1);
        stimuli.auditory(i).length = 1000*length(stimuli.auditory(i).y)/stimuli.auditory(i).fs; % Duration in ms

        % load VISUAL
        stimuli.visual(i).image_file_name = sprintf('Image%02i_ver%i.png', curr_cnd_token_number, run-1);
        stimuli.visual(i).image = imread(fullfile(path2stimuli_visual, stimuli.visual(i).image_file_name));
        stimuli.visual(i).image = Screen('MakeTexture', win, stimuli.visual(i).image);
    else
        stimuli.auditory(i).y = zeros(round(44100 * params.audio_duration * 0.9), 1);
        stimuli.visual(i).image = [];
    end
    stimuli.duration(i) = optseq_list.stimulus_duration(i);
end

stimuli.list = optseq_list;
end