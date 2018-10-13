function results = main_SLI(subject,run, params)
% Add_Psych;
%!!!!!!!!SyncTrouble!!!!!!!
Screen('Preference', 'SkipSyncTests', 1);
%!!!!!!!!SyncTrouble!!!!!!!

InitializePsychSound(1);
pahandle = PsychPortAudio('Open', 3, [], 2, 44100, 1, 0);
% pahandle = PsychPortAudio('Open', [], 1, [], FREQUENCY, CHANNELS, [], 0.015);
%%
file_name = sprintf('log_subject_%i_run_%i.txt', subject, run);
fid = fopen(fullfile('..', 'Output', file_name), 'w');
fprintf(fid,'Trial\tCond\tAudioStart\tAudioEnd\tImageEnd\tFixEnd\tAudioFN\tImageFN\tSjtChoice\tRT\n');
% Initialize
warning off
HideCursor

% FOR DEBUG ONLY (COMMENT OUT IF NOT DEBUGGING)
PsychDebugWindowConfiguration([0],[0.5])
% --------------------------------------------

rect = get(0, 'ScreenSize');
rect = [0 0 rect(3:4)];
win = Screen('OpenWindow',0,[0 0 0],rect);
% win = Screen('OpenWindow', 0, [0 0 0], [50 50 640 480]);

stimuli = load_stimuli(win, subject, run, params);

Screen(win,'TextSize',30);
% Screen('DrawText',win, intro_text, rect(3)/3, rect(4)/2,[255 255 255]);
intro_img_read = imread('../intro_slide.jpg');
intro_img = Screen('MakeTexture', win, intro_img_read, [], [], [], [], 0);
Screen('DrawTexture', win, intro_img, [], [], 0);
Screen('Flip',win);

%% Wait for a starting trigger ('t') from the MRI
% t = KbName('5');
escKey = KbName('esc');
t_pressed = false;
while ~t_pressed
    [~, ~, keyCode] = KbCheck;
    if any(keyCode([KbName('5'),KbName('5%')]))
        t_pressed = true;
    elseif keyCode(escKey)
        DisableKeysForKbCheck([]);
        Screen('CloseAll');
        return
    end
end
grandStart = tic;
DisableKeysForKbCheck(KbName('5')); % Ignores repeating t's from the MRI. Otherwise, psychtoolbox crashes
DisableKeysForKbCheck(KbName('5%'));

%% Wait several TRs before start with fixation mark
rightKey = KbName('3'); leftKey = KbName('1'); middleKey1 = KbName('2'); % middleKey2 = KbName('2');
subject_responses = cell(stimuli.num_trials, 1);
% fprintf(fid,'Grand start %f\n', clock);
Screen('DrawText',win,'*', rect(3)/2, rect(4)/2,[255 255 255]);
Screen('Flip',win); 

[sounddata, ~] = audioread(fullfile('..', 'Stimuli', 'audio', 'get_ready.wav'));
sounddata = sounddata(:,1);
PsychPortAudio('FillBuffer', pahandle, sounddata');
PsychPortAudio('Start', pahandle,1);
while toc(grandStart) < 6.5
end
PsychPortAudio('DeleteBuffer');
sounddata = stimuli.auditory(1).y(:,1);
PsychPortAudio('FillBuffer', pahandle, sounddata');    
while toc(grandStart) < params.beginning_lag
end
Screen('DrawText',win,'*', rect(3)/2, rect(4)/2,[255 255 255]);
Screen('Flip',win); 

%% Begin experiment
% try
for i = 1:stimuli.num_trials
    trial = tic;
    log_row = []; curr_row = [];
    log_row{1} = i;
    log_row{2} = stimuli.condition_name{i};
    log_row{3} = toc(grandStart);
%     fprintf(fid,'Trial %i begin time from grand start %f\n', i, toc(grandStart));
    switch stimuli.condition_name{i}
        case 'NULL'
            PsychPortAudio('DeleteBuffer');
            if i<stimuli.num_trials
                sounddata = stimuli.auditory(i+1).y(:,1);
                PsychPortAudio('FillBuffer', pahandle, sounddata');
            end
            while toc(trial) < stimuli.duration(i) % Wait
            end
            log_row{6} = toc(grandStart);
            log_row{9} = [];
            log_row{10} = -999;
        otherwise
            %% Present auditory stimulus    
            PsychPortAudio('Start', pahandle,1);   
            while toc(trial) < params.audio_duration % Wait
            end

            PsychPortAudio('DeleteBuffer');
            if i<stimuli.num_trials
                sounddata = stimuli.auditory(i+1).y(:,1);
                PsychPortAudio('FillBuffer', pahandle, sounddata');
            end
            
            log_row{4} = toc(grandStart);
%             fprintf(fid,'Trial %i audio ended from grand start: %f\n', i, toc(grandStart));
%             fprintf(fid,'Trial %i audio ended from trial start: %f\n', i, toc(trial));

            choice_str = '-'; subject_responses{i, 1, 1} = '-'; subject_responses{i, 2, 1} = -999; cnt_presses = 0;
            %% Present visual stimulus
            if ~isempty(stimuli.visual(i).image)
                Screen('DrawTexture', win, stimuli.visual(i).image);
                Screen('Flip',win);

                %% Wait for response
                rt = tic;
                while toc(trial) < params.audio_duration + params.visual_duration
                    press_event = false;
                    [~, ~, keyCode] = KbCheck;
                    if any(keyCode([rightKey,KbName('3#')]))
                        press_event = true; choice_str = '3';                                        
                    elseif any(keyCode([leftKey,KbName('1!')]))
                        press_event = true; choice_str = '1';                    
                    elseif any(keyCode([middleKey1,KbName('2@')]))
                        press_event = true; choice_str = '2';
%                     elseif any(keyCode([middleKey2,KbName('3#')]))
%                         choice_str = '3';
                    elseif keyCode(escKey)
                        DisableKeysForKbCheck([]);
                        Screen('CloseAll');
                        ShowCursor
                        return
                    end           
                    
                    if press_event
                        if cnt_presses > 0
                            if ~strcmp(subject_responses{i,1,cnt_presses}, choice_str)
                                cnt_presses = cnt_presses + 1;
                                subject_responses{i, 1, cnt_presses} = choice_str;
                                subject_responses{i, 2, cnt_presses} = toc(rt);
                            end
                        else
                            cnt_presses = cnt_presses + 1;
                            subject_responses{i, 1, cnt_presses} = choice_str;
                            subject_responses{i, 2, cnt_presses} = toc(rt);
                        end
                    end
                   
                end
            end
            log_row{5} = toc(grandStart);
%             fprintf(fid,'Trial %i image ended from grand start: %f\n', i, toc(grandStart));
%             fprintf(fid,'Trial %i image ended from trial start: %f\n', i, toc(trial));

            %% Fixation 
            DrawFormattedText(win, choice_str, 0.95*rect(3), 0.05*rect(4),[255 255 255])
            Screen('DrawText',win,'*', rect(3)/2, rect(4)/2,[255 255 255]);
            Screen('Flip',win);

            while toc(trial) < params.audio_duration + params.visual_duration + params.fixation_duration % Wait
            end
            log_row{6} = toc(grandStart);
%             fprintf(fid,'Trial %i fixation ended from grand start: %f\n', i, toc(grandStart));
%             fprintf(fid,'Trial %i fixation ended from trial start: %f\n', i, toc(trial));
            log_row{7} = stimuli.auditory(i).auditori_file_name;
            log_row{8} = stimuli.visual(i).image_file_name;
            log_row{9} = subject_responses{i, 1, 1};
            log_row{10} = subject_responses{i, 2, 1};
            
    end
    curr_row = sprintf('%i\t%s\t%0.6f\t%0.6f\t%0.6f\t%0.6f\t%s\t%s\t%s\t%0.6f', log_row{1}, log_row{2}, log_row{3}, log_row{4}, log_row{5}, log_row{6}, log_row{7}, log_row{8}, log_row{9}, log_row{10});
    fprintf(fid,'%s\n', curr_row);
    
end

last_lag = tic;
while toc(last_lag) < params.last_lag
    if toc(last_lag) < params.last_lag
        Screen('DrawText',win,'*', rect(3)/2, rect(4)/2,[255 255 255]);
        Screen('Flip',win);
    end
end

%%save data
toc(grandStart)
DisableKeysForKbCheck([]);
Screen('CloseAll');
% Remove_Psych;

results.subject_responses = subject_responses;
PsychPortAudio('Close');
fclose(fid) % close log file

ShowCursor
% catch
%     results.stimuli = stimuli;
%     results.params = params;
% end

end