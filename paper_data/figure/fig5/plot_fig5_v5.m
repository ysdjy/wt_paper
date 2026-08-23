% Fig.5 v5 (paper Fig. 4-6): shared latent representation geometry and joint probability-position
% evolution -- panel-first rebuild focused entirely on visual quality of the two 3D panels, which
% v4 rendering left "too thin/flat" (per explicit user review). All plotted values are unchanged
% real data (same shared_pca_scores_v4.csv / stage_ridges_v4.csv / confidence_ribbon_v4.csv v4
% already validated); only the RENDERING changed:
%   (d) stage-probability ridges are now SOLID VOLUMES (flat top cap at the real p_stage(x) value
%       + two vertical side walls dropping to the floor + end caps), not flat 2-sample-wide
%       curtains -- lighting now creates real shading contrast across the ridge's faces. Y-width
%       (0.40 half-span) and the side walls are pure visual extrusion, documented, never a second
%       measured dimension: every point on the top cap at a given x shares the identical real
%       Z = p_stage(x).
%   (e) confidence trajectory is now a genuine 3D TUBE (parallel-transport frame computed in
%       per-axis-normalized space, so it reads as round despite the 3 axes' different physical
%       units), not a flat ribbon. Tube radius at each point is driven by that run's real
%       `uncertainty` (documented visual encoding, no physical q-magnitude meaning); tube height
%       is always the real max_prob(x), shared around the whole circumference.
% Both panels use PCHIP interpolation (304->800 vertices) for rendering smoothness only --
% display-only, never presented as new observations; original 304-run markers are drawn on both
% surfaces so the real data stays visually traceable. Camera angles for both were chosen after
% comparing 5 candidates each (see outputs/panel_{d,e}_camera_trials/ and VISUAL_QA_V5.md).
%
% Panels (a)/(b)/(c) read the SAME shared PCA coordinates fig4(d) uses (no independent refit),
% refined for marker/legend/colorbar quality and treated as one coherent trio.
%
% Captions: every panel's "(x) description" sits BELOW that panel via annotation('textbox', ...)
% positioned from each axes' own .Position in normalized figure units, read AFTER drawnow. No
% figure-level title anywhere.
%
% Run (from the paper_data directory, non-interactively):
%   "C:\Program Files\Polyspace\R2021a\bin\matlab.exe" -nosplash -nodesktop -batch ...
%       "cd('<repo>\paper_data\figure\fig5'); plot_fig5_v5"

function plot_fig5_v5()
close all;
here = fileparts(mfilename('fullpath'));
out_dir = fullfile(here, 'outputs');
if ~exist(out_dir,'dir'); mkdir(out_dir); end

D = load_data(here);

% ---------------- standalone panel previews (panel-first workflow artifact) ----------------
render_standalone(D, out_dir);

% ---------------- final composed figure ----------------
fig = figure('Visible','off','Color','white','Units','inches','Position',[0 0 15.5 10.8]);
% Plain axes with explicit 'Position' rectangles (normalized figure units), NOT tiledlayout --
% TiledChartLayout children reject direct Position/InnerPosition/OuterPosition writes in R2021a
% (confirmed by a hard MATLAB error when attempted), which blocks exactly the post-hoc "widen this
% 3D panel so it isn't swimming in dead space" fix the brief requires. Plain axes give full manual
% control, matching the approach already proven in plot_fig5_v3.m/v4.m.
% Full vertical budget, computed explicitly so the top row's below-panel captions (which need
% ~0.107 clearance below each axes' inner box to clear both its x-tick numbers AND its own
% xlabel) land ABOVE the bottom row's 3D panels, not on top of them:
%   bottom row: y=[0.155, 0.535]   bottom-row captions: y=[0.048, 0.080]
%   top row:    y=[0.665, 0.965]   top-row captions:    y=[0.558, 0.590]   (gap to bottom row: 0.023)
ax_a = axes(fig, 'Position', [0.045 0.665 0.275 0.300]); draw_panel_a(ax_a, D);
ax_b = axes(fig, 'Position', [0.365 0.665 0.275 0.300]); draw_panel_b(ax_b, D);
ax_c = axes(fig, 'Position', [0.685 0.665 0.275 0.300]); draw_panel_c(ax_c, D);
ax_d = axes(fig, 'Position', [0.030 0.155 0.460 0.380]); draw_panel_d(ax_d, D);
ax_e = axes(fig, 'Position', [0.520 0.155 0.460 0.380]); draw_panel_e(ax_e, D);

drawnow;
add_caption_below(fig, ax_a, '(a) Shared latent PCA, colored + shaped by true stage');
add_caption_below(fig, ax_b, '(b) Same coordinates, colored by q_{true}');
add_caption_below(fig, ax_c, '(c) Same coordinates, colored by uncertainty');
add_caption_below(fig, ax_d, '(d) Stage-probability ridge volumes (y-width = visual extrusion only)');
add_caption_below(fig, ax_e, '(e) Confidence tube, radius \propto real uncertainty (no physical q-meaning)');

exportgraphics(fig, fullfile(out_dir, 'fig5_final_v5.png'), 'Resolution', 300);
exportgraphics(fig, fullfile(out_dir, 'fig5_final_v5.pdf'), 'ContentType', 'vector');
try
    print(fig, fullfile(out_dir, 'fig5_final_v5'), '-dsvg');
catch ME
    fprintf('SVG export skipped: %s\n', ME.message);
end
close(fig);
fprintf('plot_fig5_v5 done.\n');
end


function D = load_data(here)
D.pca  = readtable(fullfile(here, '..', '_shared', 'derived', 'shared_pca_scores_v4.csv'));
D.ridge = readtable(fullfile(here, 'derived', 'stage_ridges_v4.csv'));
D.conf  = readtable(fullfile(here, 'derived', 'confidence_ribbon_v4.csv'));
assert(height(D.pca) == 304, 'shared_pca_scores_v4.csv must have 304 rows');
assert(height(D.ridge) == 304, 'stage_ridges_v4.csv must have 304 rows');
assert(height(D.conf) == 304, 'confidence_ribbon_v4.csv must have 304 rows');
D.navy  = double([47 111 179])/255;
D.green = double([46 139 87])/255;
D.red   = double([231 111 81])/255;
D.darkred = double([199 54 53])/255;
D.xlims = [min(D.pca.PC1)-0.6, max(D.pca.PC1)+0.6];
D.ylims = [min(D.pca.PC2)-0.6, max(D.pca.PC2)+0.6];
end


function render_standalone(D, out_dir)
fig = figure('Visible','off','Color','white','Units','inches','Position',[0 0 4.4 4.0]);
draw_panel_a(axes(fig), D);
exportgraphics(fig, fullfile(out_dir,'panel_a_preview.png'), 'Resolution', 300); close(fig);

fig = figure('Visible','off','Color','white','Units','inches','Position',[0 0 4.4 4.0]);
draw_panel_b(axes(fig), D);
exportgraphics(fig, fullfile(out_dir,'panel_b_preview.png'), 'Resolution', 300); close(fig);

fig = figure('Visible','off','Color','white','Units','inches','Position',[0 0 4.4 4.0]);
draw_panel_c(axes(fig), D);
exportgraphics(fig, fullfile(out_dir,'panel_c_preview.png'), 'Resolution', 300); close(fig);

fig = figure('Visible','off','Color','white','Units','inches','Position',[0 0 6.5 5.2]);
draw_panel_d(axes(fig), D);
exportgraphics(fig, fullfile(out_dir,'panel_d_preview.png'), 'Resolution', 300); close(fig);

fig = figure('Visible','off','Color','white','Units','inches','Position',[0 0 6.5 5.2]);
draw_panel_e(axes(fig), D);
exportgraphics(fig, fullfile(out_dir,'panel_e_preview.png'), 'Resolution', 300); close(fig);
end


function draw_panel_a(ax, D)
hold(ax,'on');
stage_names = {'early','middle','late'};
stage_colors = [D.navy; D.green; D.red];
stage_markers = {'o','^','s'};
for s = 1:3
    m = strcmp(D.pca.true_stage, stage_names{s});
    scatter(ax, D.pca.PC1(m), D.pca.PC2(m), 24, stage_colors(s,:), stage_markers{s}, ...
            'filled', 'MarkerFaceAlpha', 0.72, 'MarkerEdgeColor', stage_colors(s,:)*0.6, 'LineWidth', 0.3);
end
for s = 1:3
    m = strcmp(D.pca.true_stage, stage_names{s});
    plot(ax, mean(D.pca.PC1(m)), mean(D.pca.PC2(m)), 'o', 'MarkerSize', 13, ...
         'MarkerEdgeColor', stage_colors(s,:)*0.55, 'LineWidth', 1.8);
end
[~, qorder] = sort(D.pca.q_true);
plot(ax, D.pca.PC1(qorder), D.pca.PC2(qorder), '--', 'Color', [0.65 0.65 0.65], 'LineWidth', 0.7);
xlim(ax, D.xlims); ylim(ax, D.ylims);
xlabel(ax,'PC1','FontName','Times New Roman','FontSize',9.5);
ylabel(ax,'PC2','FontName','Times New Roman','FontSize',9.5);
set(ax,'FontName','Times New Roman','FontSize',8.2,'LineWidth',0.7,'Box','on');
grid(ax,'on'); ax.GridAlpha=0.15;
h1 = scatter(ax, nan, nan, 24, D.navy, 'o', 'filled'); h2 = scatter(ax, nan, nan, 24, D.green, '^', 'filled');
h3 = scatter(ax, nan, nan, 24, D.red, 's', 'filled');
legend(ax, [h1 h2 h3], {'Early','Middle','Late'}, 'Location','northeast', 'FontName','Times New Roman','FontSize',7.5, 'Box','off');
end


function draw_panel_b(ax, D)
hold(ax,'on');
[~, qorder] = sort(D.pca.q_true);
plot(ax, D.pca.PC1(qorder), D.pca.PC2(qorder), '--', 'Color', [0.65 0.65 0.65], 'LineWidth', 0.7);
scatter(ax, D.pca.PC1, D.pca.PC2, 24, D.pca.q_true, 'filled', 'MarkerFaceAlpha', 0.82);
colormap(ax, turbo);
cb = colorbar(ax); cb.Label.String='q_{true}'; cb.FontName='Times New Roman'; cb.FontSize=7.5;
xlim(ax, D.xlims); ylim(ax, D.ylims);
xlabel(ax,'PC1','FontName','Times New Roman','FontSize',9.5);
ylabel(ax,'PC2','FontName','Times New Roman','FontSize',9.5);
set(ax,'FontName','Times New Roman','FontSize',8.2,'LineWidth',0.7,'Box','on');
grid(ax,'on'); ax.GridAlpha=0.15;
end


function draw_panel_c(ax, D)
hold(ax,'on');
[~, qorder] = sort(D.pca.q_true);
plot(ax, D.pca.PC1(qorder), D.pca.PC2(qorder), '--', 'Color', [0.65 0.65 0.65], 'LineWidth', 0.7);
scatter(ax, D.pca.PC1, D.pca.PC2, 24, D.pca.uncertainty, 'filled', 'MarkerFaceAlpha', 0.82);
colormap(ax, hot);
cb = colorbar(ax); cb.Label.String='uncertainty'; cb.FontName='Times New Roman'; cb.FontSize=7.5;
mis = D.pca.misclassified == 1;
plot(ax, D.pca.PC1(mis), D.pca.PC2(mis), 'o', 'MarkerSize', 9, 'MarkerEdgeColor', D.darkred, 'LineWidth', 1.5);
xlim(ax, D.xlims); ylim(ax, D.ylims);
xlabel(ax,'PC1','FontName','Times New Roman','FontSize',9.5);
ylabel(ax,'PC2','FontName','Times New Roman','FontSize',9.5);
set(ax,'FontName','Times New Roman','FontSize',8.2,'LineWidth',0.7,'Box','on');
grid(ax,'on'); ax.GridAlpha=0.15;
end


function draw_panel_d(ax, D)
hold(ax,'on');
[x_real, ord2] = sort(D.ridge.relative_life);
pE_real = D.ridge.prob_early(ord2); pM_real = D.ridge.prob_middle(ord2); pL_real = D.ridge.prob_late(ord2);
N_DISP = 800;
xq = linspace(min(x_real), max(x_real), N_DISP)';
pE_q = pchip(x_real, pE_real, xq); pM_q = pchip(x_real, pM_real, xq); pL_q = pchip(x_real, pL_real, xq);
stages = struct('y0', {0,1,2}, 'p', {pE_q,pM_q,pL_q}, 'color', {D.navy, D.green, D.red});
HALF_W = 0.40; N_Y = 9;
for s = 1:numel(stages)
    st = stages(s); y0 = st.y0; p = st.p; col = st.color;
    Ytop = linspace(y0-HALF_W, y0+HALF_W, N_Y);
    [Xg, Yg] = meshgrid(xq, Ytop);
    Zg = repmat(p', N_Y, 1);
    surf(ax, Xg, Yg, Zg, 'FaceColor', col*0.92+[1 1 1]*0.08, 'EdgeColor','none', 'FaceAlpha', 0.88, ...
         'FaceLighting','gouraud','AmbientStrength',0.35,'DiffuseStrength',0.75,'SpecularStrength',0.12);
    Xw = [xq'; xq'];
    Zw = [zeros(1,N_DISP); p'];
    surf(ax, Xw, [(y0-HALF_W)*ones(1,N_DISP); (y0-HALF_W)*ones(1,N_DISP)], Zw, ...
         'FaceColor', col*0.62, 'EdgeColor','none', 'FaceAlpha', 0.92, 'FaceLighting','gouraud','AmbientStrength',0.30,'DiffuseStrength',0.85);
    surf(ax, Xw, [(y0+HALF_W)*ones(1,N_DISP); (y0+HALF_W)*ones(1,N_DISP)], Zw, ...
         'FaceColor', col*0.78, 'EdgeColor','none', 'FaceAlpha', 0.92, 'FaceLighting','gouraud','AmbientStrength',0.30,'DiffuseStrength',0.85);
    for xi = [1, N_DISP]
        xv = xq(xi); zv = p(xi);
        surf(ax, [xv xv; xv xv], [y0-HALF_W y0+HALF_W; y0-HALF_W y0+HALF_W], [0 0; zv zv], ...
             'FaceColor', col*0.7, 'EdgeColor','none', 'FaceAlpha', 0.92, 'FaceLighting','gouraud');
    end
    plot3(ax, xq, y0*ones(size(xq)), p, 'Color', [1 1 1], 'LineWidth', 2.2);
    plot3(ax, xq, y0*ones(size(xq)), p, 'Color', col*0.55, 'LineWidth', 0.9);
    mk_idx = 1:12:length(x_real);
    p_at_real = pchip(xq, p, x_real(mk_idx));
    plot3(ax, x_real(mk_idx), y0*ones(size(mk_idx)), p_at_real, 'o', 'MarkerFaceColor','white', ...
          'MarkerEdgeColor',col*0.5,'MarkerSize',2.8,'LineWidth',0.5);
end
mixR = pE_q*D.navy(1)+pM_q*D.green(1)+pL_q*D.red(1);
mixG = pE_q*D.navy(2)+pM_q*D.green(2)+pL_q*D.red(2);
mixB = pE_q*D.navy(3)+pM_q*D.green(3)+pL_q*D.red(3);
floorY = [-0.55, 3.55];
Cf = zeros(2,N_DISP,3); Cf(1,:,1)=mixR; Cf(1,:,2)=mixG; Cf(1,:,3)=mixB; Cf(2,:,:)=Cf(1,:,:);
surf(ax, [xq';xq'], [floorY(1)*ones(1,N_DISP); floorY(2)*ones(1,N_DISP)], zeros(2,N_DISP), Cf, ...
     'EdgeColor','none','FaceAlpha',0.85,'FaceLighting','none');
[~, dom] = max([pE_q pM_q pL_q], [], 2);
plot3(ax, xq, dom-1, zeros(size(xq))+0.001, 'k-', 'LineWidth', 1.2);
set(ax,'Color','none'); grid(ax,'on'); ax.GridAlpha=0.12; ax.GridColor=[0.6 0.6 0.6]; box(ax,'off');
xlim(ax, [0 1]);
xlabel(ax,'Relative life','FontName','Times New Roman','FontSize',9.5);
set(ax,'YTick',[0 1 2],'YTickLabel',{'Early','Middle','Late'},'FontName','Times New Roman','FontSize',8.2);
zlabel(ax,'Stage probability','FontName','Times New Roman','FontSize',9.5);
zlim(ax,[0 1]); ylim(ax, floorY);
camproj(ax,'perspective');
view(ax, -35, 35);
camlight(ax,'headlight'); camlight(ax,'left'); lighting(ax,'gouraud'); material(ax,'dull');
set(ax,'FontName','Times New Roman');
end


function draw_panel_e(ax, D)
hold(ax,'on');
[life, ord3] = sort(D.conf.relative_life);
qpred = D.conf.q_pred(ord3); maxp = D.conf.max_prob(ord3); unc = D.conf.uncertainty(ord3);
N_DISP = 800;
xq2 = linspace(min(life), max(life), N_DISP)';
yq2 = pchip(life, qpred, xq2); zq2 = pchip(life, maxp, xq2); uq2 = max(pchip(life, unc, xq2), 0);
u_norm = (uq2-min(uq2))/(max(uq2)-min(uq2)+eps);
W_MIN=0.012; W_MAX=0.075; radius = W_MIN + u_norm*(W_MAX-W_MIN);
rangeX=max(xq2)-min(xq2); rangeY=max(yq2)-min(yq2); rangeZ=max(zq2)-min(zq2);
C = [xq2/rangeX, yq2/rangeY, zq2/rangeZ]; N = size(C,1);
T = zeros(N,3); T(2:end-1,:)=C(3:end,:)-C(1:end-2,:); T(1,:)=C(2,:)-C(1,:); T(end,:)=C(end,:)-C(end-1,:);
T = T ./ vecnorm(T,2,2);
N1 = zeros(N,3); B1 = zeros(N,3);
ref = [0 0 1]; v0 = ref - dot(ref,T(1,:))*T(1,:);
if norm(v0) < 1e-6; ref=[0 1 0]; v0=ref-dot(ref,T(1,:))*T(1,:); end
N1(1,:) = v0/norm(v0); B1(1,:) = cross(T(1,:), N1(1,:));
for i = 2:N
    v = N1(i-1,:) - dot(N1(i-1,:),T(i,:))*T(i,:);
    if norm(v) < 1e-8; v = B1(i-1,:) - dot(B1(i-1,:),T(i,:))*T(i,:); end
    N1(i,:) = v/norm(v); B1(i,:) = cross(T(i,:), N1(i,:));
end
M = 18; theta = linspace(0,2*pi,M);
Xt=zeros(N,M); Yt=zeros(N,M); Zt=zeros(N,M); Ct=zeros(N,M);
for i = 1:N
    circ = radius(i)*(cos(theta)'*N1(i,:) + sin(theta)'*B1(i,:));
    pts_n = C(i,:) + circ;
    Xt(i,:)=pts_n(:,1)'*rangeX; Yt(i,:)=pts_n(:,2)'*rangeY; Zt(i,:)=pts_n(:,3)'*rangeZ; Ct(i,:)=zq2(i);
end
plot3(ax, xq2, yq2, zeros(size(xq2)), '-', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.5);
for si = 1:27:N_DISP
    plot3(ax, [xq2(si) xq2(si)], [yq2(si) yq2(si)], [0 zq2(si)], '-', 'Color', [0.75 0.75 0.75], 'LineWidth', 0.55);
end
surf(ax, Xt, Yt, Zt, Ct, 'EdgeColor','none', 'FaceLighting','gouraud', 'AmbientStrength',0.32, ...
     'DiffuseStrength',0.75, 'SpecularStrength',0.25, 'SpecularExponent', 12);
colormap(ax, turbo); caxis(ax, [min(maxp) max(maxp)]);
plot3(ax, xq2, yq2, zq2, 'Color', [1 1 1], 'LineWidth', 1.6);
mk_idx2 = 1:18:length(life);
plot3(ax, life(mk_idx2), qpred(mk_idx2), maxp(mk_idx2), 'o', 'MarkerFaceColor',[1 1 1], ...
      'MarkerEdgeColor',[0.15 0.15 0.15], 'MarkerSize',3.0, 'LineWidth',0.5);
set(ax,'Color','none'); grid(ax,'on'); ax.GridAlpha=0.14; ax.GridColor=[0.6 0.6 0.6]; box(ax,'off');
xlim(ax, [min(life)-0.02, max(life)+0.02]);
ylim(ax, [min(qpred)-0.03, max(qpred)+0.03]);
xlabel(ax,'Relative life','FontName','Times New Roman','FontSize',9.5);
ylabel(ax,'q_{pred} (raw)','FontName','Times New Roman','FontSize',9.5);
zlabel(ax,'Max probability','FontName','Times New Roman','FontSize',9.5);
zlim(ax,[0 1]); camproj(ax,'perspective');
view(ax, -60, 30);
camlight(ax,'headlight'); camlight(ax,'left'); lighting(ax,'gouraud'); material(ax,'dull');
set(ax,'FontName','Times New Roman');
cb = colorbar(ax); cb.Label.String='max probability (confidence)'; cb.FontName='Times New Roman'; cb.FontSize=7.5;
end


function widen_axes(ax, wf, hf)
p = ax.Position;
cx = p(1) + p(3)/2; cy = p(2) + p(4)/2;
nw = p(3) * wf; nh = p(4) * hf;
ax.Position = [cx - nw/2, max(cy - nh/2, 0.09), nw, nh];
end


function add_caption_below(fig, ax, txt)
pos = ax.Position;  % normalized figure units, valid post-drawnow (this is the INNER plot box --
                     % x-tick number labels AND the axes' own xlabel both render further below
                     % this, in the same "outside the box" region a caption would use; pad must
                     % clear both rows, not just the tick numbers, or the caption collides with
                     % the panel's own xlabel text -- found via close visual inspection, not
                     % assumed from code alone.
x_center = pos(1) + pos(3)/2;
box_h = 0.032;
pad = 0.075;
box_bottom = max(pos(2) - pad - box_h, 0.002);
% Match the caption box width to the panel's OWN rendered width (never wider) -- prevents
% horizontal spillover into a neighboring panel's y-axis-label region, which a fixed width did.
box_w = max(pos(3) * 0.96, 0.10);
box_left = max(min(x_center - box_w/2, 1 - box_w - 0.002), 0.002);
annotation(fig, 'textbox', [box_left, box_bottom, box_w, box_h], 'String', txt, ...
    'HorizontalAlignment','center', 'VerticalAlignment','top', 'EdgeColor','none', ...
    'FontName','Times New Roman', 'FontSize', 9.5, 'FontWeight','bold', 'Interpreter','tex');
end
