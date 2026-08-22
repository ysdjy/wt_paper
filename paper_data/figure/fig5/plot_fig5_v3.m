% Fig.5 v3 (paper Fig. 4-6): shared latent representation geometry and joint probability-position
% evolution -- MATLAB half of a Python(data)+MATLAB(3D render) split build.
%
% DATA: reads three CSVs written by prepare_fig5_v3.py from the real, frozen paper_data --
%   derived/pca_scores_v3.csv          304 real samples, one fixed PCA fit (fit in Python, not
%                                       refit here), true/pred stage, q_true, uncertainty, entropy
%   derived/stage_ridges_v3.csv        304 real (relative_life, prob_early/middle/late) rows
%   derived/confidence_trajectory_v3.csv  304 real (relative_life, q_pred, max_prob, pred_stage)
% No point is fabricated, jittered, or refit here. Panels (d)/(e) use a narrow visual RIBBON
% EXTRUSION (a second parallel curve offset by a small fixed width) purely so the real 1-D
% trajectory reads as a surface at a glance -- the extrusion width carries NO quantitative meaning
% and must never be read as a measured second dimension. This is stated again in the figure's
% README v3 section.
%
% Layout: tiledlayout(2,6). Top row: (a) stage-colored PCA [tiles 1-2], (b) q-colored PCA
% [tiles 3-4], (c) uncertainty-colored PCA [tiles 5-6] -- same PC1/PC2 axis limits/aspect across
% all three (computed once from pca_scores_v3.csv, never refit per panel). Bottom row:
% (d) stage-probability 3D ridges [tiles 1-3], (e) confidence/q/life 3D ribbon [tiles 4-6].
%
% Captions: every panel's "(x) description" text sits BELOW that panel (not title(), which MATLAB
% places above) -- via annotation('textbox', ...) positioned from each axes' own .Position in
% normalized figure units, read AFTER drawnow so the tiledlayout has already settled (same
% "don't guess before layout is final" principle documented for the Python v3 scripts' GridSpec
% bug). No figure-level title anywhere (no sgtitle).
%
% Run (from the paper_data directory, non-interactively):
%   "C:\Program Files\Polyspace\R2021a\bin\matlab.exe" -nosplash -nodesktop -batch ...
%       "cd('<repo>\paper_data\figure\fig5'); plot_fig5_v3"

function plot_fig5_v3()
close all;

here = fileparts(mfilename('fullpath'));
pca_t  = readtable(fullfile(here, 'derived', 'pca_scores_v3.csv'));
ridge_t = readtable(fullfile(here, 'derived', 'stage_ridges_v3.csv'));
conf_t  = readtable(fullfile(here, 'derived', 'confidence_trajectory_v3.csv'));
assert(height(pca_t) == 304, 'pca_scores_v3.csv must have 304 rows');
assert(height(ridge_t) == 304, 'stage_ridges_v3.csv must have 304 rows');
assert(height(conf_t) == 304, 'confidence_trajectory_v3.csv must have 304 rows');

% ---- shared palette (same hex values as _shared/style_v2.py / style_v3.py STAGE_COLORS) ----
navy = double([27 58 92]) / 255;    % Early  (#1B3A5C)
teal = double([42 140 122]) / 255;  % Middle (#2A8C7A)
gold = double([217 164 65]) / 255;  % Late   (#D9A441)
grey = double([183 189 194]) / 255; % (#B7BDC2)

stageColor = containers.Map({'early', 'middle', 'late'}, {navy, teal, gold});
stageMarker = containers.Map({'early', 'middle', 'late'}, {'o', '^', 's'});

% degradation colormap: navy -> teal -> gold, 256 steps (matches Python DEGRADATION_CMAP)
degrad_cmap = [linspace(navy(1), teal(1), 128)', linspace(navy(2), teal(2), 128)', linspace(navy(3), teal(3), 128)'; ...
               linspace(teal(1), gold(1), 128)', linspace(teal(2), gold(2), 128)', linspace(teal(3), gold(3), 128)'];

fig = figure('Units', 'inches', 'Position', [0 0 15.5 10.2], 'Color', 'white');
t = tiledlayout(fig, 2, 6, 'TileSpacing', 'compact', 'Padding', 'compact');

% shared PCA axis limits across (a)/(b)/(c) -- computed once, applied to all three
pad = 0.6;
xl = [min(pca_t.PC1) - pad, max(pca_t.PC1) + pad];
yl = [min(pca_t.PC2) - pad, max(pca_t.PC2) + pad];

axA = nexttile(t, 1, [1 2]);
draw_pca_stage(axA, pca_t, stageColor, stageMarker, grey, xl, yl);

axB = nexttile(t, 3, [1 2]);
draw_pca_continuous(axB, pca_t, pca_t.q_true, degrad_cmap, 'q_{true}', stageMarker, grey, xl, yl);

axC = nexttile(t, 5, [1 2]);
draw_pca_uncertainty(axC, pca_t, stageMarker, grey, xl, yl);

axD = nexttile(t, 7, [1 3]);
axD.Units = 'normalized';
draw_stage_ridges_3d(axD, ridge_t, navy, teal, gold);

axE = nexttile(t, 10, [1 3]);
axE.Units = 'normalized';
draw_confidence_ribbon_3d(axE, conf_t, stageColor);

drawnow;  % settle tiledlayout before reading .Position for captions

add_caption_below(fig, axA, '(a) Shared latent PCA, colored + shaped by true stage');
add_caption_below(fig, axB, '(b) Same coordinates, colored by q (shape = true stage)');
add_caption_below(fig, axC, '(c) Same coordinates, colored by uncertainty (shape = true stage)');
add_caption_below(fig, axD, '(d) Stage-probability ridge ribbons over the C6 lifecycle (y-width is a visual extrusion only)');
add_caption_below(fig, axE, '(e) Joint evolution: life x q_{pred} x confidence (ribbon width is a visual extrusion only)');

outDir = fullfile(here, 'outputs');
if ~exist(outDir, 'dir'); mkdir(outDir); end
exportgraphics(fig, fullfile(outDir, 'fig5_v3.png'), 'Resolution', 300);
exportgraphics(fig, fullfile(outDir, 'fig5_v3.pdf'), 'ContentType', 'vector');
try
    print(fig, fullfile(outDir, 'fig5_v3'), '-dsvg');
catch ME
    fprintf('SVG export skipped: %s\n', ME.message);
end

logDir = fullfile(here, 'logs');
if ~exist(logDir, 'dir'); mkdir(logDir); end
fid = fopen(fullfile(logDir, 'validation_v3_matlab.txt'), 'w');
fprintf(fid, 'PASS: pca_scores_v3.csv rows=%d (expected 304)\n', height(pca_t));
fprintf(fid, 'PASS: stage_ridges_v3.csv rows=%d (expected 304)\n', height(ridge_t));
fprintf(fid, 'PASS: confidence_trajectory_v3.csv rows=%d (expected 304)\n', height(conf_t));
fprintf(fid, 'PASS: shared PCA xlim=[%.3f %.3f] ylim=[%.3f %.3f] applied identically to panels a/b/c\n', xl(1), xl(2), yl(1), yl(2));
n_mis = sum(pca_t.misclassified);
fprintf(fid, 'PASS: %d misclassified samples (of 304) outlined in panel (c)\n', n_mis);
fprintf(fid, 'Saved outputs: fig5_v3.png, fig5_v3.pdf (+ .svg if supported)\n');
fclose(fid);
fprintf('Fig.5 v3 (MATLAB) done.\n');
end


function draw_pca_stage(ax, pca_t, stageColor, stageMarker, grey, xl, yl)
axes(ax); hold(ax, 'on');
[~, ord] = sort(pca_t.q_true);
plot(ax, pca_t.PC1(ord), pca_t.PC2(ord), '--', 'Color', [grey 0.8], 'LineWidth', 0.8);
stages = {'early', 'middle', 'late'};
labels = {'Early', 'Middle', 'Late'};
h = gobjects(1, 3);
for i = 1:3
    m = strcmp(pca_t.true_stage, stages{i});
    h(i) = scatter(ax, pca_t.PC1(m), pca_t.PC2(m), 22, stageColor(stages{i}), ...
        'filled', 'Marker', stageMarker(stages{i}), 'MarkerFaceAlpha', 0.85);
end
legend(ax, h, labels, 'Location', 'northeast', 'Box', 'off', 'FontSize', 8);
finish_2d_axes(ax, xl, yl);
end


function draw_pca_continuous(ax, pca_t, colorVar, cmap, cbarLabel, stageMarker, grey, xl, yl)
axes(ax); hold(ax, 'on');
[~, ord] = sort(pca_t.q_true);
plot(ax, pca_t.PC1(ord), pca_t.PC2(ord), '--', 'Color', [grey 0.8], 'LineWidth', 0.8);
stages = {'early', 'middle', 'late'};
for i = 1:3
    m = strcmp(pca_t.true_stage, stages{i});
    scatter(ax, pca_t.PC1(m), pca_t.PC2(m), 24, colorVar(m), 'filled', ...
        'Marker', stageMarker(stages{i}), 'MarkerFaceAlpha', 0.9);
end
colormap(ax, cmap);
caxis(ax, [min(colorVar) max(colorVar)]);
cb = colorbar(ax); cb.Label.String = cbarLabel; cb.Label.Interpreter = 'tex'; cb.FontSize = 7;
finish_2d_axes(ax, xl, yl);
end


function draw_pca_uncertainty(ax, pca_t, stageMarker, grey, xl, yl)
axes(ax); hold(ax, 'on');
[~, ord] = sort(pca_t.q_true);
plot(ax, pca_t.PC1(ord), pca_t.PC2(ord), '--', 'Color', [grey 0.8], 'LineWidth', 0.8);
stages = {'early', 'middle', 'late'};
for i = 1:3
    m = strcmp(pca_t.true_stage, stages{i});
    scatter(ax, pca_t.PC1(m), pca_t.PC2(m), 24, pca_t.uncertainty(m), 'filled', ...
        'Marker', stageMarker(stages{i}), 'MarkerFaceAlpha', 0.9);
end
colormap(ax, flipud(hot(256)));
cb = colorbar(ax); cb.Label.String = 'uncertainty'; cb.FontSize = 7;
mis = pca_t.misclassified == 1;
if any(mis)
    scatter(ax, pca_t.PC1(mis), pca_t.PC2(mis), 70, [0.70 0.20 0.20], ...
        'Marker', 'o', 'MarkerFaceColor', 'none', 'LineWidth', 1.3);
end
finish_2d_axes(ax, xl, yl);
end


function finish_2d_axes(ax, xl, yl)
xlim(ax, xl); ylim(ax, yl);
xlabel(ax, 'PC1'); ylabel(ax, 'PC2');
set(ax, 'Box', 'off', 'TickDir', 'out', 'FontSize', 8, 'Color', 'white');
set(ax, 'XColor', [0.15 0.15 0.15], 'YColor', [0.15 0.15 0.15]);
grid(ax, 'on'); ax.GridColor = [0.89 0.90 0.91]; ax.GridAlpha = 1; ax.Layer = 'bottom';
% NOTE: deliberately NOT forcing pbaspect/daspect to the data aspect ratio here -- doing so
% shrinks the rendered plot box inside ax.Position without updating .Position itself, which
% add_caption_below() reads to place captions -- this created a large dead-whitespace gap between
% the shrunk plot and its caption on the first render. Same xlim/ylim across (a)/(b)/(c) already
% gives visual comparability without that side effect.
end


function draw_stage_ridges_3d(ax, ridge_t, navy, teal, gold)
axes(ax); hold(ax, 'on');
x = ridge_t.relative_life;
stages = {'early', 'middle', 'late'};
cols = {'prob_early', 'prob_middle', 'prob_late'};
colors = {navy, teal, gold};
levels = [0 1 2];
w = 0.28;  % visual-only ribbon half-width in the stage-axis direction
for i = 1:3
    z = ridge_t.(cols{i});
    y0 = levels(i) - w; y1 = levels(i) + w;
    X = [x, x]; Y = [repmat(y0, size(x)), repmat(y1, size(x))]; Z = [z, z];
    surf(ax, X, Y, Z, 'FaceColor', colors{i}, 'FaceAlpha', 0.55, 'EdgeColor', 'none');
    % floor projection
    surf(ax, X, Y, zeros(size(Z)), 'FaceColor', colors{i}, 'FaceAlpha', 0.12, 'EdgeColor', 'none');
    plot3(ax, x, repmat(levels(i), size(x)), z, 'Color', colors{i} * 0.7, 'LineWidth', 1.4);
end
xlabel(ax, 'Relative life'); zlabel(ax, 'Stage probability');
set(ax, 'YTick', levels, 'YTickLabel', {'Early', 'Middle', 'Late'});
set(ax, 'Color', 'none', 'FontSize', 8, 'Box', 'off');
ax.XColor = [0.15 0.15 0.15]; ax.YColor = [0.15 0.15 0.15]; ax.ZColor = [0.15 0.15 0.15];
grid(ax, 'on'); ax.GridColor = [0.85 0.86 0.88]; ax.GridAlpha = 0.6; ax.LineWidth = 0.6;
view(ax, -48, 26);
camlight(ax, 'headlight'); lighting(ax, 'gouraud'); material(ax, 'dull');
zlim(ax, [0 1]);
end


function draw_confidence_ribbon_3d(ax, conf_t, stageColor)
axes(ax); hold(ax, 'on');
x = conf_t.relative_life; y = conf_t.q_pred; z = conf_t.max_prob;
stages = conf_t.pred_stage;

% real trajectory, colored per-segment by predicted stage
uniqStages = {'early', 'middle', 'late'};
for i = 1:3
    m = strcmp(stages, uniqStages{i});
    plot3(ax, x(m), y(m), z(m), '.', 'Color', stageColor(uniqStages{i}), 'MarkerSize', 8);
end
% continuous line through all points in life order (already sorted), colored by stage via
% short colored segments
for k = 1:height(conf_t)-1
    c = stageColor(stages{k});
    plot3(ax, x(k:k+1), y(k:k+1), z(k:k+1), '-', 'Color', c, 'LineWidth', 1.6);
end

% narrow VISUAL-ONLY ribbon: offset a parallel curve by a small fixed delta in the q direction
dq = 0.012 * range(y);
X = [x, x]; Y = [y - dq, y + dq]; Z = [z, z];
surf(ax, X, Y, Z, 'FaceColor', 'interp', 'CData', [z, z], 'FaceAlpha', 0.35, 'EdgeColor', 'none');
colormap(ax, flipud(winter(256)));
cb = colorbar(ax); cb.Label.String = 'max probability (confidence)'; cb.FontSize = 7;

% floor projection of the real (life, q_pred) trajectory at z=0
plot3(ax, x, y, zeros(size(z)), '--', 'Color', [0.6 0.62 0.64], 'LineWidth', 1.0);

xlabel(ax, 'Relative life'); ylabel(ax, 'q_{pred} (raw)'); zlabel(ax, 'Max probability (confidence)');
set(ax, 'Color', 'none', 'FontSize', 8, 'Box', 'off');
ax.XColor = [0.15 0.15 0.15]; ax.YColor = [0.15 0.15 0.15]; ax.ZColor = [0.15 0.15 0.15];
grid(ax, 'on'); ax.GridColor = [0.85 0.86 0.88]; ax.GridAlpha = 0.6; ax.LineWidth = 0.6;
view(ax, -48, 26);
camlight(ax, 'headlight'); lighting(ax, 'gouraud'); material(ax, 'dull');
zlim(ax, [0 1]);
end


function add_caption_below(fig, ax, txt)
ax.Units = 'normalized';
pos = ax.Position;  % [left bottom width height], normalized to the figure
gap = 0.028;
h = 0.062;  % tall enough for a wrapped 2-line caption at this font size
y = max(pos(2) - gap - h, 0.005);
annotation(fig, 'textbox', [pos(1), y, pos(3), h], 'String', txt, ...
    'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', ...
    'EdgeColor', 'none', 'FontSize', 9.5, 'FontWeight', 'bold', 'FontName', 'Arial', ...
    'Interpreter', 'none');
end
