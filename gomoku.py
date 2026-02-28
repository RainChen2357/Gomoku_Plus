import tkinter as tk
from tkinter import messagebox
import random

class Gomoku:
    # UI 配色与字体
    FONT_UI = ("Microsoft YaHei UI", "PingFang SC", "Helvetica Neue", "Arial")
    COLOR_BG = "#1a1a1a"
    COLOR_BOARD = "#c4a574"
    COLOR_GRID = "#5c4033"
    COLOR_STAR = "#3d2914"
    COLOR_STONE_BLACK = "#2d2d2d"
    COLOR_STONE_WHITE = "#f5f5f0"
    COLOR_GHOST_BLACK = "#666666"
    COLOR_GHOST_WHITE = "#b0b0b0"
    COLOR_ACCENT = "#c9a227"
    COLOR_BTN = "#8b4513"
    COLOR_BTN_HOVER = "#a0522d"

    def __init__(self, root, board_size=15):
        self.root = root
        self.root.title("五子棋 Gomoku")
        self.root.configure(bg=self.COLOR_BG)
        self.root.minsize(400, 520)
        self.board_size = board_size
        self.cell_size = 40  # 像素 (每个网格的大小)
        self.margin = self.cell_size  # 像素 (边缘留白)

        # 计算画布总尺寸
        self.canvas_size = (self.board_size - 1) * self.cell_size + 2 * self.margin

        # 棋盘状态: 0=空, 1=黑棋, 2=白棋
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        # 每格棋子的 canvas id，用于随机消失时删除
        self.stone_ids = [[None] * self.board_size for _ in range(self.board_size)]

        # 玩家状态: 1=黑棋先下
        self.current_player = 1
        self.game_over = False
        # 连下两颗：0=无，1=本回合已触发，可再下一子
        self.double_move_remaining = 0
        # 虚影：当前虚影的 canvas id 与所在格子
        self.ghost_id = None
        self.ghost_cell = None

        # 初始化 UI 元素
        self.setup_ui()

    def setup_ui(self):
        # 0. 上方标题与提示区
        top_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        top_frame.pack(pady=(16, 0))
        title = tk.Label(top_frame, text="五子棋", font=(self.FONT_UI[0], 20, "bold"), fg=self.COLOR_ACCENT, bg=self.COLOR_BG)
        title.pack()
        self.bonus_label = tk.Label(top_frame, text="", font=(self.FONT_UI[0], 11, "bold"), fg="#e74c3c", bg=self.COLOR_BG)
        self.bonus_label.pack(pady=(4, 0))

        # 0'. 概率调节（随时生效）
        prob_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        prob_frame.pack(pady=(8, 4))
        tk.Label(prob_frame, text="连下两颗", font=(self.FONT_UI[0], 9), fg="#a0a0a0", bg=self.COLOR_BG).pack(side=tk.LEFT, padx=(0, 4))
        self.prob_double_scale = tk.Scale(
            prob_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=80,
            showvalue=True, bg=self.COLOR_BG, fg="#e0e0e0", troughcolor="#444",
            highlightthickness=0, font=(self.FONT_UI[0], 8)
        )
        self.prob_double_scale.set(10)
        self.prob_double_scale.pack(side=tk.LEFT, padx=(0, 2))
        tk.Label(prob_frame, text="%", font=(self.FONT_UI[0], 9), fg="#a0a0a0", bg=self.COLOR_BG).pack(side=tk.LEFT, padx=(0, 16))
        tk.Label(prob_frame, text="随机消失", font=(self.FONT_UI[0], 9), fg="#a0a0a0", bg=self.COLOR_BG).pack(side=tk.LEFT, padx=(0, 4))
        self.prob_disappear_scale = tk.Scale(
            prob_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=80,
            showvalue=True, bg=self.COLOR_BG, fg="#e0e0e0", troughcolor="#444",
            highlightthickness=0, font=(self.FONT_UI[0], 8)
        )
        self.prob_disappear_scale.set(10)
        self.prob_disappear_scale.pack(side=tk.LEFT, padx=(0, 2))
        tk.Label(prob_frame, text="%", font=(self.FONT_UI[0], 9), fg="#a0a0a0", bg=self.COLOR_BG).pack(side=tk.LEFT)

        # 1. 画布（木质棋盘 + 细边框）
        self.canvas = tk.Canvas(
            self.root, width=self.canvas_size, height=self.canvas_size,
            bg=self.COLOR_BOARD, highlightthickness=0
        )
        self.canvas.pack(pady=12, padx=16)

        # 2. 绘制网格
        self.draw_grid()

        # 3. 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", self.on_leave)

        # 4. 底部状态与按钮
        bottom_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        bottom_frame.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.status_label = tk.Label(
            bottom_frame, text="轮到 黑棋 下子",
            font=(self.FONT_UI[0], 12), fg="#e0e0e0", bg=self.COLOR_BG
        )
        self.status_label.pack(side=tk.LEFT)

        reset_btn = tk.Button(
            bottom_frame, text="重新开始", command=self.reset_game,
            font=(self.FONT_UI[0], 10), bg=self.COLOR_BTN, fg="white",
            activebackground=self.COLOR_BTN_HOVER, activeforeground="white",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2"
        )
        reset_btn.pack(side=tk.RIGHT)

    def draw_grid(self):
        """绘制 15x15 的网格线"""
        grid_color = self.COLOR_GRID
        w = 1
        for i in range(self.board_size):
            y = self.margin + i * self.cell_size
            self.canvas.create_line(self.margin, y, self.canvas_size - self.margin, y, fill=grid_color, width=w)
        for i in range(self.board_size):
            x = self.margin + i * self.cell_size
            self.canvas.create_line(x, self.margin, x, self.canvas_size - self.margin, fill=grid_color, width=w)

        star_points = [3, 7, 11] if self.board_size == 15 else []
        for r in star_points:
            for c in star_points:
                self.draw_star_point(r, c)

    def draw_star_point(self, r, c):
        """绘制星点"""
        x = self.margin + c * self.cell_size
        y = self.margin + r * self.cell_size
        r2 = 3
        self.canvas.create_oval(x - r2, y - r2, x + r2, y + r2, fill=self.COLOR_STAR, outline="")

    def clear_ghost(self):
        """移除当前虚影"""
        if self.ghost_id is not None:
            self.canvas.delete(self.ghost_id)
            self.ghost_id = None
            self.ghost_cell = None

    def draw_ghost(self, row, col):
        """在指定格子绘制当前方虚影（半透明效果用浅色模拟）"""
        self.clear_ghost()
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        radius = self.cell_size // 2 - 2
        if self.current_player == 1:
            fill_color, outline_color = self.COLOR_GHOST_BLACK, "#444"
        else:
            fill_color, outline_color = self.COLOR_GHOST_WHITE, "#888"
        self.ghost_id = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=fill_color, outline=outline_color, width=1
        )
        self.ghost_cell = (row, col)

    def on_motion(self, event):
        """鼠标移动：在合法空位上显示当前方虚影"""
        if self.game_over:
            return
        x_grid = round((event.x - self.margin) / self.cell_size)
        y_grid = round((event.y - self.margin) / self.cell_size)
        if 0 <= x_grid < self.board_size and 0 <= y_grid < self.board_size:
            if self.board[y_grid][x_grid] == 0 and self.ghost_cell != (y_grid, x_grid):
                self.draw_ghost(y_grid, x_grid)
        else:
            self.clear_ghost()

    def on_leave(self, event):
        """鼠标离开画布时移除虚影"""
        self.clear_ghost()

    def on_click(self, event):
        """处理鼠标点击：确定下棋位置"""
        if self.game_over:
            return

        # 1. 将画布点击坐标转换成棋盘网格坐标
        x_grid = round((event.x - self.margin) / self.cell_size)
        y_grid = round((event.y - self.margin) / self.cell_size)

        # 2. 检查边界：是否在网格范围内
        if 0 <= x_grid < self.board_size and 0 <= y_grid < self.board_size:
            # 3. 检查：是否已经是落子点
            if self.board[y_grid][x_grid] == 0:
                self.clear_ghost()
                self.place_stone(y_grid, x_grid)

    def remove_random_previous_stone(self, exclude_row, exclude_col):
        """按当前设定概率，从本步之前已有的棋子中随机消失一个（不包含刚下的 exclude）"""
        prob = self.prob_disappear_scale.get() / 100.0
        if prob <= 0 or random.random() >= prob:
            return
        # 收集本步之前已有的所有棋子（排除刚下的那一格）
        candidates = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] != 0 and (r, c) != (exclude_row, exclude_col):
                    candidates.append((r, c))
        if not candidates:
            return
        r, c = random.choice(candidates)
        if self.stone_ids[r][c] is not None:
            for oid in self.stone_ids[r][c]:
                self.canvas.delete(oid)
            self.stone_ids[r][c] = None
        self.board[r][c] = 0

    def place_stone(self, row, col):
        """核心逻辑：落子，随机消失，检查状态，切换玩家"""
        # A. 更新二维数组状态
        self.board[row][col] = self.current_player

        # B. 在画布上绘制棋子（带轻微立体感），并记录 id
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        radius = self.cell_size // 2 - 2
        if self.current_player == 1:
            fill_color, outline_color = self.COLOR_STONE_BLACK, "#1a1a1a"
        else:
            fill_color, outline_color = self.COLOR_STONE_WHITE, "#ccc"
        shadow_off = 2
        shadow_id = self.canvas.create_oval(
            x - radius + shadow_off, y - radius + shadow_off,
            x + radius + shadow_off, y + radius + shadow_off,
            fill="#333" if self.current_player == 1 else "#999", outline=""
        )
        main_id = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=fill_color, outline=outline_color, width=1
        )
        self.stone_ids[row][col] = (shadow_id, main_id)

        # B'. 有 10% 概率令之前下过的某一颗子（黑白均可）随机消失
        self.remove_random_previous_stone(row, col)

        # C. 检查获胜条件（以当前棋盘为准：落子后能否连成五子）
        if self.check_win(row, col):
            self.game_over = True
            self.bonus_label.config(text="")
            winner = "黑棋 (Black)" if self.current_player == 1 else "白棋 (White)"
            self.status_label.config(text=f"游戏结束！{winner} 获胜", fg="#e74c3c", font=(self.FONT_UI[0], 13, "bold"))
            messagebox.showinfo("游戏结束", f"{winner} 获胜！🎉")
        
        # D. 检查和棋（棋盘下满）
        elif self.is_board_full():
            self.game_over = True
            self.bonus_label.config(text="")
            self.status_label.config(text="游戏结束！和棋", fg="#3498db")
            messagebox.showinfo("游戏结束", "和棋！")

        # E. 连下两颗判定与切换玩家
        else:
            if self.double_move_remaining == 1:
                # 已用过连下两颗，本子落完正常换手
                self.double_move_remaining = 0
                self.bonus_label.config(text="")
                self.current_player = 3 - self.current_player
                player_name = "黑棋 (Black)" if self.current_player == 1 else "白棋 (White)"
                self.status_label.config(text=f"轮到 {player_name} 下子")
            else:
                # 按当前设定概率获得连下两颗
                prob = self.prob_double_scale.get() / 100.0
                if prob > 0 and random.random() < prob:
                    self.double_move_remaining = 1
                    self.bonus_label.config(text="🎲 连下两颗！请再下一子")
                    player_name = "黑棋 (Black)" if self.current_player == 1 else "白棋 (White)"
                    self.status_label.config(text=f"轮到 {player_name} 再下一子（连下两颗）")
                else:
                    self.current_player = 3 - self.current_player
                    self.bonus_label.config(text="")
                    player_name = "黑棋 (Black)" if self.current_player == 1 else "白棋 (White)"
                    self.status_label.config(text=f"轮到 {player_name} 下子")

    def check_win(self, r, c):
        """从最新落子点出发，检查四个方向"""
        player = self.board[r][c]
        # 四个方向：水平、垂直、主对角线（右下）、副对角线（右上）
        directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]

        for dr, dc in directions:
            count = 1  # 基础：当前落下的这一颗子

            # 沿着一个方向延伸
            count += self.count_consecutive(r, c, dr, dc, player)
            # 沿着相反方向延伸
            count += self.count_consecutive(r, c, -dr, -dc, player)

            # 是否达到五子连珠
            if count >= 5:
                return True
        return False

    def count_consecutive(self, start_r, start_c, dr, dc, player):
        """辅助函数：沿某一方向计算相同颜色棋子的数量"""
        count = 0
        curr_r, curr_c = start_r + dr, start_c + dc
        # 循环检查：在边界内，且棋子颜色相同
        while 0 <= curr_r < self.board_size and 0 <= curr_c < self.board_size and \
              self.board[curr_r][curr_c] == player:
            count += 1
            curr_r += dr
            curr_c += dc
        return count

    def is_board_full(self):
        """检查棋盘是否还有空位"""
        for row in self.board:
            if 0 in row:
                return False
        return True

    def reset_game(self):
        """重置所有状态到初始"""
        self.game_over = False
        self.current_player = 1
        self.double_move_remaining = 0
        self.ghost_id = None
        self.ghost_cell = None
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.stone_ids = [[None] * self.board_size for _ in range(self.board_size)]

        self.bonus_label.config(text="")
        self.canvas.delete("all")
        self.draw_grid()
        self.status_label.config(text="轮到 黑棋 下子", fg="#e0e0e0", font=(self.FONT_UI[0], 12))

# 游戏运行入口
if __name__ == "__main__":
    root = tk.Tk()
    game = Gomoku(root, board_size=15)
    root.mainloop()