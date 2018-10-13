function params = load_params(run)
    %% General params
%     params.num_trials = 5; 
    params.TR = 2.5; %in sec

    %% Time durations
    params.beginning_lag = 4*params.TR;
    params.last_lag = 3*params.TR;
    params.audio_duration = params.TR; %s
    params.fixation_duration = 0.3; % [sec]
    params.visual_duration = 2*params.TR - params.fixation_duration; %s

    %% Stimuli
    load('stim_order_per_run.mat');
    params.stim_numbers = stim_numbers.(sprintf('run%i', run));
    for cnd = {'ZM', 'SVOZ', 'SZVO', 'OVS', 'MIDDLE'} % Shuffle stimuli order
        randvec = randperm(length(params.stim_numbers.(cnd{1})));
        params.stim_numbers.(cnd{1}) = params.stim_numbers.(cnd{1})(randvec);
    end
%     params.OVS_allowed_token_numbers = 1:20; % Only OVS with male subject
    params.MIDDLE_filler_positions = [1:2, 4, 7];
end
