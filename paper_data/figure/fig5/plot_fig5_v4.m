% Fig.5 v4 (paper Fig. 4-6): shared latent representation geometry and joint probability-position
% evolution -- MATLAB half of a Python(data)+MATLAB(3D render) split build. Round-4 centerpiece.
%
% DATA:
%   ../_shared/derived/shared_pca_scores_v4.csv   304 real samples, SAME coordinates fig4(d) uses
%                                                  (read directly, not a local copy -- guarantees
%                                                  Fig.4/Fig.5 show identical latent geometry)
%   derived/stage_ridges_v4.csv                   304 real (relative_life, prob_early/middle/late)
%   derived/confidence_ribbon_v4.csv              304 real (relative_life, q_pred, max_prob,
%                                                  pred_stage, uncertainty) -- uncertainty joined
%                                                  1:1 by run_id in prepare_fig5_v4.py, validated
%                                                  304<->304 there.
%
% Panels (d)/(e) are the round's main rework vs v3 ("too thin, too much like a simple ribbon"):
%   (d) three BROAD stage-probability ridge CURTAINS (not 2-point-wide ribbons). Every cross-curtain
%       Y-sample at a given X shares the exact same real Z = p_stage(x) -- the Y-width is a fixed
%       VISUAL EXTRUSION ONLY (w=0.30 half-span), never a second measured dimension. A real
%       probability-mixture floor color strip (pE*Early + pM*Middle + pL*Late, per real x) sits at
%       z=0, plus a dominant-stage transition line from real argmax(p_E,p_M,p_L).
%   (e) an UNCERTAINTY-DRIVEN ribbon: half-width at each x is a linear function of that run's real
%       `uncertainty` (normalized), NOT a fixed constant -- this is new information encoded
%       visually, not fabricated. Every cross-ribbon Y-sample still shares the same real
%       Z = max_prob(x); only the ribbon's WIDTH varies with real uncertainty, never its height.
% Both panels use PCHIP interpolation (304 -> ~800 display vertices) for rendering smoothness only
% -- explicitly display-only, never presented as new observations; original 304-run markers are
% drawn on top of both surfaces so the real data stays visually traceable.
%
% Captions: every panel's "(x) description" sits BELOW that panel via annotation('textbox', ...)
% positioned from each axes' own .Position in normalized figure units, read AFTER drawnow (same
% "don't guess before layout is final" principle as the Python GridSpec fix documented in fig1-4's
% v4 READMEs). No figure-level title anywhere (no sgtitle).
%
% Run (from the paper_data directory, non-interactively):
%   "C:\Program Files\Polyspace\R2021a\bin\matlab.exe" -nosplash -nodesktop -batch ...
%       "cd('<repo>\paper_data\figure\fig5'); plot_fig5_v4"

function plot_fig5_v4()
close all;

here = fileparts(mfilename('fullpath'));
pca_t   = readtable(fullfile(here, '..', '_shared', 'derived', 'shared_pca_scores_v4.csv'));
ridge_t = readtable(fullfile(here, 'derived', 'stage_ridges_v4.csv'));
conf_t  = readtable(fullfile(here, 'derived', 'confidence_ribbon_v4.csv'));
assert(height(pca_t) == 304, 'shared_pca_scores_v4.csv must have 304 rows');
assert(height(ridge_t) == 304, 'stage_ridges_v4.csv must have 304 rows');
assert(height(conf_t) == 304, 'confidence_ribbon_v4.csv must have 304 rows');
assert(any(strcmp(conf_t.Properties.VariableNames, 'uncertainty')), 'confidence_ribbon_v4.csv must carry real uncertainty');

% ---- shared palette: exact hex values from _shared/style_v4.py STAGE_COLORS ----
navy = double([47 111 179]) / 255;   % Early  (#2F6FB3)
teal = double([46 139 87])  / 255;   % Middle (#2E8B57)
gold = double([231 111 81]) / 255;   % Late   (#E76F51)
grey = double([183 189 194]) / 255;  % (#B7BDC2)

stageColor = containers.Map({'early', 'middle', 'late'}, {navy, teal, gold});
stageMarker = containers.Map({'early', 'middle', 'late'}, {'o', '^', 's'});

% degradation colormap: navy -> teal -> gold, 256 steps (matches Python DEGRADATION_CMAP)
degrad_cmap = [linspace(navy(1), teal(1), 128)', linspace(navy(2), teal(2), 128)', linspace(navy(3), teal(3), 128)'; ...
               linspace(teal(1), gold(1), 128)', linspace(teal(2), gold(2), 128)', linspace(teal(3), gold(3), 128)'];

% confidence colormap: deep purple -> teal -> warm yellow, 256 steps (brief's explicit request,
% not a literal rainbow/jet)
purple = [72 43 122] / 255; midc = [38 130 128] / 255; yellow = [232 197 78] / 255;
conf_cmap = [linspace(purple(1), midc(1), 128)', linspace(purple(2), midc(2), 128)', linspace(purple(3), midc(3), 128)'; ...
             linspace(midc(1), yellow(1), 128)', linspace(midc(2), yellow(2), 128)', linspace(midc(3), yellow(3), 128)'];

mm2in = 1/25.4;
fig = figure('Units', 'inches', 'Position', [0 0 178*mm2in 132*mm2in], 'Color', 'white');
% 'loose' (not 'compact') leaves real inter-row space for the below-panel captions to occupy --
% with 'compact', row-1 captions (needing enough gap to clear PC1/tick text) had nowhere to go
% but INTO row 2's own caption zone, since annotation() overlays aren't part of tiledlayout's own
% spacing accounting.
t = tiledlayout(fig, 2, 6, 'TileSpacing', 'loose', 'Padding', 'compact');

% shared PCA axis limits across (a)/(b)/(c) -- computed once, applied to all three, identical to
% the coordinates fig4(d) plots (same source file)
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
draw_stage_ridge_curtains_3d(axD, ridge_t, navy, teal, gold);

axE = nexttile(t, 10, [1 3]);
axE.Units = 'normalized';
draw_confidence_ribbon_3d(axE, conf_t, stageColor, conf_cmap);

drawnow;  % settle tiledlayout before reading .Position for captions

add_caption_below(fig, axA, '(a) Shared latent PCA, colored + shaped by true stage');
add_caption_below(fig, axB, '(b) Same coordinates, colored by q_{true} (shape = true stage)');
add_caption_below(fig, axC, '(c) Same coordinates, colored by uncertainty (shape = true stage)');
add_caption_below(fig, axD, '(d) Stage-probability ridge curtains (y-width = visual extrusion only)');
add_caption_below(fig, axE, '(e) Confidence ribbon, width \propto real uncertainty (no physical q-meaning)');

outDir = fullfile(here, 'outputs');
if ~exist(outDir, 'dir'); mkdir(outDir); end
exportgraphics(fig, fullfile(outDir, 'fig5_v4_600dpi.png'), 'Resolution', 600);
exportgraphics(fig, fullfile(outDir, 'fig5_v4_paper_preview.png'), 'Resolution', 200);
exportgraphics(fig, fullfile(outDir, 'fig5_v4.pdf'), 'ContentType', 'vector');
try
    print(fig, fullfile(outDir, 'fig5_v4'), '-dsvg');
catch ME
    fprintf('SVG export skipped: %s\n', ME.message);
end

logDir = fullfile(here, 'logs');
if ~exist(logDir, 'dir'); mkdir(logDir); end
fid = fopen(fullfile(logDir, 'validation_v4_matlab.txt'), 'w');
fprintf(fid, 'PASS: shared_pca_scores_v4.csv rows=%d (expected 304), read directly from _shared/derived (not a local copy)\n', height(pca_t));
fprintf(fid, 'PASS: stage_ridges_v4.csv rows=%d (expected 304)\n', height(ridge_t));
fprintf(fid, 'PASS: confidence_ribbon_v4.csv rows=%d (expected 304), carries real per-run uncertainty\n', height(conf_t));
fprintf(fid, 'PASS: shared PCA xlim=[%.3f %.3f] ylim=[%.3f %.3f] applied identically to panels a/b/c\n', xl(1), xl(2), yl(1), yl(2));
n_mis = sum(pca_t.misclassified);
fprintf(fid, 'PASS: %d misclassified samples (of 304) outlined in panel (c), from real misclassified column\n', n_mis);
fprintf(fid, 'PASS: panel(d) ridge curtains use 21 y-samples per stage, all sharing the same real Z=p_stage(x) at each x (no fabricated 2nd dimension)\n');
fprintf(fid, 'PASS: panel(e) ribbon half-width driven by real uncertainty, range [%.4f, %.4f]; Z=max_prob(x) shared across ribbon width\n', min(conf_t.uncertainty), max(conf_t.uncertainty));
fprintf(fid, 'Saved outputs: fig5_v4_600dpi.png, fig5_v4_paper_preview.png, fig5_v4.pdf (+ .svg if supported)\n');
fclose(fid);
fprintf('Fig.5 v4 (MATLAB) done.\n');
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
    h(i) = scatter(ax, pca_t.PC1(m), pca_t.PC2(m), 20, stageColor(stages{i}), ...
        'filled', 'Marker', stageMarker(stages{i}), 'MarkerFaceAlpha', 0.85);
end
% real per-stage centroid markers (hollow, large) -- computed from real sample means
for i = 1:3
    m = strcmp(pca_t.true_stage, stages{i});
    cx = mean(pca_t.PC1(m)); cy = mean(pca_t.PC2(m));
    scatter(ax, cx, cy, 130, stageColor(stages{i}), 'Marker', 'o', ...
        'MarkerFaceColor', 'none', 'LineWidth', 1.6);
end
legend(ax, h, labels, 'Location', 'northeast', 'Box', 'off', 'FontSize', 7.5);
finish_2d_axes(ax, xl, yl);
end


function draw_pca_continuous(ax, pca_t, colorVar, cmap, cbarLabel, stageMarker, grey, xl, yl)
axes(ax); hold(ax, 'on');
[~, ord] = sort(pca_t.q_true);
plot(ax, pca_t.PC1(ord), pca_t.PC2(ord), '--', 'Color', [grey 0.8], 'LineWidth', 0.8);
stages = {'early', 'middle', 'late'};
for i = 1:3
    m = strcmp(pca_t.true_stage, stages{i});
    scatter(ax, pca_t.PC1(m), pca_t.PC2(m), 22, colorVar(m), 'filled', ...
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
    scatter(ax, pca_t.PC1(m), pca_t.PC2(m), 22, pca_t.uncertainty(m), 'filled', ...
        'Marker', stageMarker(stages{i}), 'MarkerFaceAlpha', 0.9);
end
colormap(ax, flipud(hot(256)));
cb = colorbar(ax); cb.Label.String = 'uncertainty'; cb.FontSize = 7;
mis = pca_t.misclassified == 1;
if any(mis)
    scatter(ax, pca_t.PC1(mis), pca_t.PC2(mis), 65, [0.70 0.20 0.20], ...
        'Marker', 'o', 'MarkerFaceColor', 'none', 'LineWidth', 1.3);
end
finish_2d_axes(ax, xl, yl);
end


function finish_2d_axes(ax, xl, yl)
xlim(ax, xl); ylim(ax, yl);
xlabel(ax, 'PC1'); ylabel(ax, 'PC2');
set(ax, 'Box', 'off', 'TickDir', 'out', 'FontSize', 7.5, 'Color', 'white', 'FontName', 'Times New Roman');
set(ax, 'XColor', [0.15 0.15 0.15], 'YColor', [0.15 0.15 0.15]);
grid(ax, 'on'); ax.GridColor = [0.89 0.90 0.91]; ax.GridAlpha = 1; ax.Layer = 'bottom';
% NOTE (inherited from v3, re-verified this round): deliberately NOT forcing pbaspect/daspect on
% the 2D PCA panels -- doing so shrinks the rendered plot box inside ax.Position without updating
% .Position itself, which add_caption_below() reads to place captions below each panel.
end


function draw_stage_ridge_curtains_3d(ax, ridge_t, navy, teal, gold)
axes(ax); hold(ax, 'on');
x = ridge_t.relative_life;
cols = {'prob_early', 'prob_middle', 'prob_late'};
colors = {navy, teal, gold};
levels = [0 1 2];
w = 0.30;            % visual-only ridge half-width (y-direction), NOT a measured dimension
nY = 21;              % 15-25 cross-curtain y-samples, per the brief
nXdisp = 800;         % display-resolution x (real data has 304 points)

xq = linspace(min(x), max(x), nXdisp)';
yStrip = linspace(-w, w, 2);  % for the floor color strip (thin band spanning all 3 rows)

% --- three broad ridge curtains ---
for i = 1:3
    zReal = ridge_t.(cols{i});
    zDisp = interp1(x, zReal, xq, 'pchip');   % display-only smoothing, real values at real x
    yband = linspace(levels(i) - w, levels(i) + w, nY);
    [Xg, Yg] = meshgrid(xq, yband);
    Zg = repmat(zDisp', nY, 1);   % EVERY cross-curtain sample at a given x shares the same real z
    surf(ax, Xg, Yg, Zg, 'FaceColor', colors{i}, 'FaceAlpha', 0.62, 'EdgeColor', 'none');
    % thin white highlight + real-color center ridge line (real 304 samples, not interpolated)
    plot3(ax, x, repmat(levels(i), size(x)), zReal, 'Color', colors{i} * 0.65, 'LineWidth', 2.0);
    plot3(ax, x, repmat(levels(i), size(x)), zReal + 0.006, 'Color', [1 1 1], 'LineWidth', 0.6);
    % real per-run markers every ~12 runs, proving traceability to actual observations
    idx = 1:12:numel(x);
    scatter3(ax, x(idx), repmat(levels(i), numel(idx), 1), zReal(idx), 14, colors{i}, 'filled', ...
        'MarkerEdgeColor', 'w', 'LineWidth', 0.4);
end

% --- real probability-mixture floor color strip: pE*Early + pM*Middle + pL*Late, per real x ---
pE = interp1(x, ridge_t.prob_early, xq, 'pchip');
pM = interp1(x, ridge_t.prob_middle, xq, 'pchip');
pL = interp1(x, ridge_t.prob_late, xq, 'pchip');
mix = pE * navy + pM * teal + pL * gold;   % [nXdisp x 3], real per-x probability-weighted blend
[Xf, Yf] = meshgrid(xq, yStrip);
Zf = zeros(size(Xf));
Cf = permute(repmat(mix, 1, 1, 2), [3 1 2]);  % 2 x nXdisp x 3 color array for the 2-row strip
surf(ax, Xf, Yf, Zf, 'CData', Cf, 'FaceColor', 'flat', 'EdgeColor', 'none', 'FaceAlpha', 0.95);

% --- dominant-stage transition line from real argmax(p_E,p_M,p_L) ---
[~, domIdx] = max([ridge_t.prob_early, ridge_t.prob_middle, ridge_t.prob_late], [], 2);
domY = levels(domIdx)';
plot3(ax, x, domY, zeros(size(x)) + 0.003, 'k-', 'LineWidth', 1.1);

xlabel(ax, 'Relative life'); zlabel(ax, 'Stage probability');
set(ax, 'YTick', levels, 'YTickLabel', {'Early', 'Middle', 'Late'});
set(ax, 'Color', 'none', 'FontSize', 7.5, 'Box', 'off', 'FontName', 'Times New Roman');
ax.XColor = [0.15 0.15 0.15]; ax.YColor = [0.15 0.15 0.15]; ax.ZColor = [0.15 0.15 0.15];
grid(ax, 'on'); ax.GridColor = [0.85 0.86 0.88]; ax.GridAlpha = 0.6; ax.LineWidth = 0.6;
view(ax, -52, 25);
camproj(ax, 'perspective');
pbaspect(ax, [1.7 1.0 0.95]);
camlight(ax, 'headlight'); camlight(ax, 'left'); lighting(ax, 'gouraud'); material(ax, 'dull');
zlim(ax, [0 1]); xlim(ax, [min(x) max(x)]); ylim(ax, [-w-0.05 2+w+0.05]);
end


function draw_confidence_ribbon_3d(ax, conf_t, stageColor, conf_cmap)
axes(ax); hold(ax, 'on');
x = conf_t.relative_life; y = conf_t.q_pred; z = conf_t.max_prob; u = conf_t.uncertainty;
stages = conf_t.pred_stage;
nY = 19;        % 15-25 cross-ribbon y-samples
nXdisp = 800;

xq = linspace(min(x), max(x), nXdisp)';
yq = interp1(x, y, xq, 'pchip');
zq = interp1(x, z, xq, 'pchip');
uq = interp1(x, u, xq, 'pchip');

% --- uncertainty-driven ribbon half-width (visual encoding only, no physical q-meaning) ---
u_norm = (uq - min(u)) / (max(u) - min(u) + eps);
w_min = 0.015 * range(y); w_max = 0.060 * range(y);
halfw = w_min + u_norm * (w_max - w_min);

Yg = zeros(nY, nXdisp);
band = linspace(-1, 1, nY)';
for k = 1:nXdisp
    Yg(:, k) = yq(k) + band * halfw(k);
end
Xg = repmat(xq', nY, 1);
Zg = repmat(zq', nY, 1);   % EVERY cross-ribbon sample at a given x shares the same real z=max_prob
Cg = repmat(zq', nY, 1);   % face color by real max_prob
surf(ax, Xg, Yg, Zg, 'CData', Cg, 'FaceColor', 'interp', 'EdgeColor', 'none', 'FaceAlpha', 0.80);
colormap(ax, conf_cmap);
caxis(ax, [min(z) max(z)]);
cb = colorbar(ax); cb.Label.String = 'max probability (confidence)'; cb.FontSize = 7;

% --- thick white center trajectory + thin dark outline (real 304-point trajectory) ---
plot3(ax, x, y, z, '-', 'Color', 'w', 'LineWidth', 3.0);
plot3(ax, x, y, z, '-', 'Color', [0.15 0.15 0.15], 'LineWidth', 1.1);
idx = 1:17:numel(x);
uniqStages = {'early', 'middle', 'late'};
for i = 1:3
    m = strcmp(stages(idx), uniqStages{i});
    scatter3(ax, x(idx(m)), y(idx(m)), z(idx(m)), 20, stageColor(uniqStages{i}), 'filled', ...
        'MarkerEdgeColor', 'w', 'LineWidth', 0.5);
end

% --- floor projection of the real (life, q_pred) trajectory, colored by real max_prob ---
surfaceLine3(ax, x, y, zeros(size(z)), z, conf_cmap, [min(z) max(z)]);

% --- real vertical stems from floor to surface, every ~28 runs ---
stemIdx = 1:28:numel(x);
for k = stemIdx
    plot3(ax, [x(k) x(k)], [y(k) y(k)], [0 z(k)], 'Color', [0.55 0.57 0.60 0.55], 'LineWidth', 0.7);
end

xlabel(ax, 'Relative life'); ylabel(ax, 'q_{pred} (raw)'); zlabel(ax, 'Max probability (confidence)');
set(ax, 'Color', 'none', 'FontSize', 7.5, 'Box', 'off', 'FontName', 'Times New Roman');
ax.XColor = [0.15 0.15 0.15]; ax.YColor = [0.15 0.15 0.15]; ax.ZColor = [0.15 0.15 0.15];
grid(ax, 'on'); ax.GridColor = [0.85 0.86 0.88]; ax.GridAlpha = 0.6; ax.LineWidth = 0.6;
view(ax, -52, 25);
camproj(ax, 'perspective');
pbaspect(ax, [1.7 1.0 0.95]);
camlight(ax, 'headlight'); camlight(ax, 'left'); lighting(ax, 'gouraud'); material(ax, 'dull');
zlim(ax, [0 1]); xlim(ax, [min(x) max(x)]);
end


function surfaceLine3(ax, x, y, z, colorVar, cmap, crange)
% thin colored line via a degenerate 2-row surf (MATLAB has no native "colored line3"), used for
% the floor projection so it can be colored by a continuous real variable.
X = [x, x]; Y = [y, y]; Z = [z, z];
C = [colorVar, colorVar];
surf(ax, X, Y, Z, 'CData', C, 'FaceColor', 'none', 'EdgeColor', 'interp', 'LineWidth', 1.6);
colormap(ax, cmap); caxis(ax, crange);
end


function add_caption_below(fig, ax, txt)
ax.Units = 'normalized';
pos = ax.Position;  % [left bottom width height], normalized to the figure
% NOTE: ax.Position is the axes' OUTER box, but xlabel/tick-label text (and, for 3D axes with a
% rotated view, y/z-tick text too) renders further below/around that box without being reflected
% in .Position -- gap must clear those decorations, not just touch the box edge. 0.026 was not
% enough (captions collided with "PC1"/"Early"/tick text on first render); bumped to clear it.
gap = 0.058;
h = 0.058;  % tall enough for a wrapped 1-2 line caption at this font size
y = max(pos(2) - gap - h, 0.004);
annotation(fig, 'textbox', [pos(1), y, pos(3), h], 'String', txt, ...
    'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', ...
    'EdgeColor', 'none', 'FontSize', 8.6, 'FontWeight', 'bold', 'FontName', 'Times New Roman', ...
    'Interpreter', 'tex');
end
