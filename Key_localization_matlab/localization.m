%% Main Key Localization Logic

% Load Data
T = readCANLogFixed('path_to_log.log', anchorNames, SCALE_FACTOR);
uniqueTimes = unique(T.Time,'stable');

% --- Initialize Kalman Filters for distances ---
kf_dist = struct();
for ai = 1:4
    kf_dist(ai).x = 5; kf_dist(ai).P = 10;
    kf_dist(ai).Q = 1e-5; kf_dist(ai).R = 1e-2;
    kf_dist(ai).initialized = false;
end

prevPosition = [];
timeStep = 0.1;

% Main Loop
for tIdx = 1:numel(uniqueTimes)
    tstr = uniqueTimes{tIdx};
    subset = T(strcmp(T.Time,tstr),:);

    % Extract raw distances 
    rawDists = nan(4,1);
    for ai = 1:4
        rows = subset(strcmp(subset.CAN_ID, anchorNames{ai}),:);
        if ~isempty(rows)
            rawDists(ai) = rows.Distance(1);
        end
    end

    % Distance Filtering (Kalman and spike filtering)
    kfEst = nan(4,1);
    for ai = 1:4
        if isnan(rawDists(ai)), continue; end
        kf = kf_dist(ai);
        if ~kf.initialized
            kf.x = rawDists(ai); kf.P = 1; kf.initialized = true;
        else
            kf.P = kf.P + kf.Q;
            innovation = rawDists(ai) - kf.x;
            if abs(innovation) < SPIKE_THRESHOLD || kf.P > 5
                K = kf.P / (kf.P + kf.R);
                kf.x = kf.x + K * innovation;
                kf.P = (1-K)*kf.P;
            end
        end
        kf_dist(ai) = kf;
        kfEst(ai) = kf.x;
    end

    % Position Estimation (Trilateration)
    validIdx = find(~isnan(kfEst));
    if numel(validIdx) < 2, continue; end
    if numel(validIdx) == 2
        B = twoAnchorTrilateration(anchors(validIdx,:), kfEst(validIdx));
    else
        B = trilateration_ls(anchors(validIdx,:), kfEst(validIdx));
    end

    % Velocity-based Outlier Rejection
    if ~isempty(prevPosition)
        v = norm(B - prevPosition) / timeStep;
        if v > MAX_VELOCITY, B = prevPosition; end
    end

  

