% Panel (d) v5 standalone: stage-probability ridges rendered as SOLID VOLUMES (top cap + two
% side walls dropping to the floor), not flat curtains. Every value used for real geometry (the
% top cap's Z, the side walls' top edge) is the exact real p_stage(x) from stage_ridges_v4.csv --
% the Y half-width and the side walls' existence are pure visual extrusion (never a second
% measured dimension); PCHIP interpolation (304->800) is display-resolution only, real 304
% run markers are drawn on top so the underlying observations stay traceable.
%
% This script renders panel (d) ALONE, at several candidate camera angles, so each can be
% inspected independently before picking one for the final composition (per the mandated
% panel-first, multi-angle workflow).
function panel_d_standalone_v5()
close all;
here = fileparts(mfilename('fullpath'));
ridge_t = readtable(fullfile(here, 'derived', 'stage_ridges_v4.csv'));
assert(height(ridge_t) == 304, 'stage_ridges_v4.csv must have 304 real rows');

navy  = double([47 111 179])/255;   % Early
green = double([46 139 87])/255;    % Middle
red   = double([231 111 81])/255;   % Late

x_real = ridge_t.relative_life;
pE_real = ridge_t.prob_early;
pM_real = ridge_t.prob_middle;
pL_real = ridge_t.prob_late;
[x_real, ord] = sort(x_real); pE_real = pE_real(ord); pM_real = pM_real(ord); pL_real = pL_real(ord);

% Display-only PCHIP resolution increase (304 -> 800), documented, never used for any stat.
N_DISP = 800;
xq = linspace(min(x_real), max(x_real), N_DISP)';
pE_q = pchip(x_real, pE_real, xq);
pM_q = pchip(x_real, pM_real, xq);
pL_q = pchip(x_real, pL_real, xq);

stages = struct('name', {'Early','Middle','Late'}, 'y0', {0,1,2}, 'p', {pE_q,pM_q,pL_q}, ...
                 'color', {navy, green, red});

HALF_W = 0.40;   % visual-only half width of the ridge "loaf" (documented, not a measured axis)
N_Y = 9;         % cross-ribbon samples for the TOP cap only (all share identical real Z at each x)

angles_to_try = [-52 25; -40 20; -60 30; -35 35; -65 18];

for a = 1:size(angles_to_try,1)
    fig = figure('Visible','off','Color','white','Units','inches','Position',[0 0 6.5 5.2]);
    ax = axes(fig); hold(ax,'on');
    for s = 1:numel(stages)
        st = stages(s);
        y0 = st.y0; p = st.p; col = st.color;

        % ---- TOP CAP: flat across Y at each x, Z = real p(x) exactly (only real values here) ----
        Ytop = linspace(y0-HALF_W, y0+HALF_W, N_Y);
        [Xg, Yg] = meshgrid(xq, Ytop);
        Zg = repmat(p', N_Y, 1);   % every row identical -- same real Z at a given x, by construction
        top_shade = col * 0.92 + [1 1 1]*0.08;
        surf(ax, Xg, Yg, Zg, 'FaceColor', top_shade, 'EdgeColor','none', 'FaceAlpha', 0.88, ...
             'FaceLighting','gouraud','AmbientStrength',0.35,'DiffuseStrength',0.75,'SpecularStrength',0.12);

        % ---- SIDE WALLS: purely geometric vertical drop from the real top height to the floor
        % (z=0). No new "measured" value is introduced -- each wall's top edge equals the same
        % real p(x) used for the top cap; the bottom edge is the floor (z=0) by construction. ----
        wall_shade_left  = col * 0.62;
        wall_shade_right = col * 0.78;
        Xw = [xq'; xq'];
        Yw_left  = [ (y0-HALF_W)*ones(1,N_DISP); (y0-HALF_W)*ones(1,N_DISP) ];
        Yw_right = [ (y0+HALF_W)*ones(1,N_DISP); (y0+HALF_W)*ones(1,N_DISP) ];
        Zw = [ zeros(1,N_DISP); p' ];
        surf(ax, Xw, Yw_left,  Zw, 'FaceColor', wall_shade_left,  'EdgeColor','none', 'FaceAlpha', 0.92, ...
             'FaceLighting','gouraud','AmbientStrength',0.30,'DiffuseStrength',0.85);
        surf(ax, Xw, Yw_right, Zw, 'FaceColor', wall_shade_right, 'EdgeColor','none', 'FaceAlpha', 0.92, ...
             'FaceLighting','gouraud','AmbientStrength',0.30,'DiffuseStrength',0.85);

        % ---- end caps (x_min, x_max) so the ridge reads as a closed solid, not an open shell ----
        for xi = [1, N_DISP]
            xv = xq(xi); zv = p(xi);
            Xc = [xv xv; xv xv];
            Yc = [y0-HALF_W y0+HALF_W; y0-HALF_W y0+HALF_W];
            Zc = [0 0; zv zv];
            surf(ax, Xc, Yc, Zc, 'FaceColor', col*0.7, 'EdgeColor','none', 'FaceAlpha', 0.92, ...
                 'FaceLighting','gouraud');
        end

        % ---- real center ridge line + real run markers every ~12 runs (traceability to 304 obs) ----
        plot3(ax, xq, y0*ones(size(xq)), p, 'Color', [1 1 1], 'LineWidth', 2.4);
        plot3(ax, xq, y0*ones(size(xq)), p, 'Color', col*0.55, 'LineWidth', 1.0);
        mk_idx = 1:12:length(x_real);
        p_at_real = pchip(xq, p, x_real(mk_idx));
        plot3(ax, x_real(mk_idx), y0*ones(size(mk_idx)), p_at_real, 'o', ...
              'MarkerFaceColor','white','MarkerEdgeColor',col*0.5,'MarkerSize',3.2,'LineWidth',0.6);

        % ---- real probability-mixture floor strip (documented real color blend, not texture) ----
    end

    % floor probability-mixture strip: color = pE*navy + pM*green + pL*red at each real x (304 pts)
    mixR = pE_q*navy(1) + pM_q*green(1) + pL_q*red(1);
    mixG = pE_q*navy(2) + pM_q*green(2) + pL_q*red(2);
    mixB = pE_q*navy(3) + pM_q*green(3) + pL_q*red(3);
    floorY = [-0.55, 3.55];
    Xf = [xq'; xq'];
    Yf = [floorY(1)*ones(1,N_DISP); floorY(2)*ones(1,N_DISP)];
    Zf = zeros(2, N_DISP);
    Cf = zeros(2, N_DISP, 3);
    Cf(1,:,1)=mixR; Cf(1,:,2)=mixG; Cf(1,:,3)=mixB; Cf(2,:,:)=Cf(1,:,:);
    surf(ax, Xf, Yf, Zf, Cf, 'EdgeColor','none','FaceAlpha',0.85,'FaceLighting','none');

    % dominant-stage transition line on the floor (argmax(p_E,p_M,p_L) per real x)
    [~, dom] = max([pE_q pM_q pL_q], [], 2);
    dom_y = (dom-1);  % 0=Early,1=Middle,2=Late matches stage y0
    plot3(ax, xq, dom_y, zeros(size(xq))+0.001, 'k-', 'LineWidth', 1.3);

    set(ax,'Color','none');
    grid(ax,'on'); ax.GridAlpha = 0.12; ax.GridColor = [0.6 0.6 0.6];
    box(ax,'off');
    xlabel(ax,'Relative life','FontName','Times New Roman','FontSize',10);
    set(ax,'YTick',[0 1 2],'YTickLabel',{'Early','Middle','Late'},'FontName','Times New Roman','FontSize',9);
    zlabel(ax,'Stage probability','FontName','Times New Roman','FontSize',10);
    zlim(ax,[0 1]);
    ylim(ax, floorY);
    pbaspect(ax, [1.8 1.0 0.85]);
    camproj(ax,'perspective');
    view(ax, angles_to_try(a,1), angles_to_try(a,2));
    camlight(ax,'headlight');
    camlight(ax, 'left');
    lighting(ax,'gouraud');
    material(ax,'dull');
    set(ax,'FontName','Times New Roman');

    outp = fullfile(here, 'outputs', 'panel_d_camera_trials', sprintf('angle_%d_az%d_el%d.png', a, angles_to_try(a,1), angles_to_try(a,2)));
    if ~exist(fileparts(outp),'dir'); mkdir(fileparts(outp)); end
    exportgraphics(fig, outp, 'Resolution', 200);
    close(fig);
    fprintf('Rendered %s\n', outp);
end
fprintf('panel_d_standalone_v5 done.\n');
end
