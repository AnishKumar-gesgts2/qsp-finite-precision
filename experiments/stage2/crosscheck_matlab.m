function crosscheck_matlab(qsppack_root, input_path, output_path)
% Run the ORIGINAL MATLAB QSPPACK on the exported Stage 2 cases.
% Saves each completed case so a browser/session interruption can be resumed.
% Example from the project root, after checking out the pinned QSPPACK source:
% addpath('experiments/stage2');
% crosscheck_matlab('C:/path/to/QSPPACK');

    assert(exist('OCTAVE_VERSION', 'builtin') == 0 && ~isempty(ver('MATLAB')), ...
        'This check requires actual MATLAB; other runtimes must not be labeled MATLAB.');
    project_root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    if nargin < 2
        input_path = fullfile(project_root, 'results', 'stage2', 'matlab_input.json');
    end
    if nargin < 3
        output_path = fullfile(project_root, 'results', 'stage2', 'matlab_output.json');
    end
    addpath(genpath(qsppack_root));
    request = jsondecode(fileread(input_path));
    names = fieldnames(request.expected_source_hashes);
    actual_hashes = struct();
    for k = 1:numel(names)
        name = names{k};
        source_path = which(name);
        assert(~isempty(source_path), 'Missing original QSPPACK function: %s', name);
        actual_hashes.(name) = normalized_sha256(source_path);
        assert(strcmp(actual_hashes.(name), request.expected_source_hashes.(name)), ...
            'Source hash mismatch for %s; use the pinned original MATLAB QSPPACK revision.', name);
    end
    result = struct('runtime', 'MATLAB', 'runtime_version', version, ...
                    'input_sha256', raw_sha256(input_path), ...
                    'source_revision', request.source_revision, 'source_hashes', actual_hashes, ...
                    'convention_cases', struct([]), 'cases', struct([]));
    if isfile(output_path)
        previous = jsondecode(fileread(output_path));
        if isfield(previous, 'input_sha256') && strcmp(previous.input_sha256, result.input_sha256) ...
                && strcmp(previous.runtime, 'MATLAB') && strcmp(previous.runtime_version, version) ...
                && isequal(previous.source_hashes, actual_hashes)
            if ~isempty(previous.cases)
                result.cases = previous.cases;
            end
            if isfield(previous, 'convention_cases') && ~isempty(previous.convention_cases)
                result.convention_cases = previous.convention_cases;
            end
        end
    end
    for k = 1:numel(request.convention_cases)
        entry = request.convention_cases(k);
        if numel(result.convention_cases) >= k && strcmp(result.convention_cases(k).case_id, entry.case_id)
            continue;
        end
        opts = struct('method', 'Newton', 'criteria', request.criteria, ...
                      'maxiter', request.maxiter, 'useReal', true, ...
                      'targetPre', entry.targetPre, 'typePhi', 'full');
        [phases, info] = QSP_solver(entry.coefficients(:), entry.parity, opts);
        response = QSPGetEntry(entry.x(:), phases, info);
        result.convention_cases(k) = struct('case_id', entry.case_id, ...
            'full_phases', phases(:).', 'x', entry.x(:).', 'response', response(:).', ...
            'solver_value', info.value, 'iterations', info.iter, ...
            'targetPre', entry.targetPre, 'typePhi', 'full');
        fprintf('Stage 1 %s: MATLAB residual %.3e\n', entry.case_id, info.value);
        write_report(output_path, result);
    end
    for k = 1:numel(request.cases)
        entry = request.cases(k);
        if numel(result.cases) >= k && strcmp(result.cases(k).case_id, entry.case_id)
            fprintf('%s: reused completed MATLAB case\n', entry.case_id);
            continue;
        end
        opts = struct('method', 'Newton', 'criteria', request.criteria, ...
                      'maxiter', request.maxiter, 'useReal', true, ...
                      'targetPre', true, 'typePhi', 'full');
        [phases, info] = QSP_solver(entry.coefficients(:), entry.parity, opts);
        x = entry.audit_x(:);
        response = QSPGetEntry(x, phases, info);
        validation_x = entry.validation_x(:);
        validation_response = QSPGetEntry(validation_x, phases, info);
        output = struct('case_id', entry.case_id, 'full_phases', phases(:).', ...
                        'audit_x', x(:).', 'response', response(:).', ...
                        'solver_value', info.value, 'iterations', info.iter, ...
                        'targetPre', true, 'typePhi', 'full', ...
                        'validation_x', validation_x(:).', ...
                        'validation_response', validation_response(:).', ...
                        'solver_seconds', info.time);
        result.cases(k) = output;
        fprintf('%s: MATLAB QSPPACK residual %.3e\n', entry.case_id, info.value);
        write_report(output_path, result);
    end
    fprintf('Saved %d original MATLAB cross-checks to %s\n', numel(result.cases), output_path);
end

function write_report(output_path, result)
    file = fopen(output_path, 'w', 'n', 'UTF-8');
    assert(file ~= -1, 'Cannot open output file');
    cleanup = onCleanup(@() fclose(file)); %#ok<NASGU>
    fprintf(file, '%s\n', jsonencode(result));
end

function digest = raw_sha256(path)
    file = fopen(path, 'rb');
    assert(file ~= -1, 'Cannot open MATLAB input');
    bytes = fread(file, Inf, '*uint8');
    fclose(file);
    algorithm = java.security.MessageDigest.getInstance('SHA-256');
    algorithm.update(typecast(bytes, 'int8'));
    digest = lower(reshape(dec2hex(typecast(algorithm.digest(), 'uint8'), 2).', 1, []));
end

function digest = normalized_sha256(path)
    file = fopen(path, 'r', 'n', 'UTF-8');
    assert(file ~= -1, 'Cannot open QSPPACK source');
    text = fscanf(file, '%c', [1 Inf]);
    fclose(file);
    text = strrep(strrep(text, sprintf('\r\n'), sprintf('\n')), sprintf('\r'), sprintf('\n'));
    algorithm = java.security.MessageDigest.getInstance('SHA-256');
    algorithm.update(typecast(uint8(unicode2native(text, 'UTF-8')), 'int8'));
    bytes = typecast(algorithm.digest(), 'uint8');
    digest = lower(reshape(dec2hex(bytes, 2).', 1, []));
end
