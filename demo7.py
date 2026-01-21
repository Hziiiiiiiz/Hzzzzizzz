from manim import *
import argparse
import sys
import os


class VerticalMultiplicationWithAddition(Scene):
    def __init__(self, num1=123, num2=45, digit_width=0.8, **kwargs):
        super().__init__(**kwargs)
        self.num1 = num1
        self.num2 = num2
        self.digit_width = digit_width
        self.result_font_size = 36

    def construct(self):
        num1, num2 = self.num1, self.num2
        str_num1, str_num2 = str(num1), str(num2)

        # ------------------- 第一行：被乘数 -------------------
        digits1 = [Integer(int(d), color=WHITE, font_size=36) for d in str_num1]
        top_line = VGroup(*digits1)
        top_line.arrange(RIGHT, buff=self.digit_width).shift(UP * 1.0)

        # ------------------- 第二行：× 和乘数 -------------------
        digits2 = [Integer(int(d), color=WHITE, font_size=36) for d in str_num2]
        second_line = VGroup(*digits2)
        second_line.arrange(RIGHT, buff=self.digit_width)
        second_line.next_to(top_line, DOWN, buff=0.6, aligned_edge=RIGHT)

        leftmost_x = top_line.get_left()[0]
        times_symbol = MathTex("\\times", font_size=48).move_to(
            np.array([leftmost_x - 0.6, second_line.get_center()[1], 0])
        )

        # 横线1
        line_left = top_line.get_left() + LEFT * 0.5
        line_right = top_line.get_right() + RIGHT * 0.5
        underline1 = Line(line_left, line_right).next_to(second_line, DOWN, buff=0.2)

        self.play(Write(top_line), Write(times_symbol), Write(second_line))
        self.play(Create(underline1))
        self.wait(0.5)

        # ------------------- 列对齐系统（右对齐）-------------------
        rightmost_x = top_line[-1].get_center()[0]

        def get_column_x(col_index_from_right):
            return rightmost_x - col_index_from_right * self.digit_width

        max_cols = len(str_num1) + len(str_num2) + 2

        # ------------------- 存储每一行中间结果 Mobjects -------------------
        partial_rows = []
        partial_values = []  # 存储每个部分积数值（用于后续加法）

        # ------------------- 逐位相乘动画 -------------------
        for idx, d2_char in enumerate(reversed(str_num2)):
            d2 = int(d2_char)
            carry = 0
            result_digits_mobs = []
            row_y = underline1.get_bottom()[1] - 0.8 * (idx + 1)

            # 高亮当前乘数位
            digit_to_highlight = digits2[-(idx + 1)]
            self.play(digit_to_highlight.animate.set_color(YELLOW), run_time=0.5)

            # 从右到左遍历被乘数
            for j, d1_char in enumerate(reversed(str_num1)):
                d1 = int(d1_char)
                pos_j = len(str_num1) - 1 - j
                product = d1 * d2 + carry
                digit_val = product % 10
                carry = product // 10

                target_col = j + idx
                x_pos = get_column_x(target_col)
                final_pos = np.array([x_pos, row_y, 0])

                result_digit = Integer(digit_val, color=BLUE, font_size=32).move_to(final_pos)

                # 高亮相乘数字
                d1_digit = digits1[pos_j]
                self.play(d1_digit.animate.set_color(YELLOW), run_time=0.4)

                temp = Integer(product, color=PURPLE, font_size=28).move_to(result_digit.get_center())
                self.play(FadeIn(temp, scale=0.7), run_time=0.2)
                self.play(Transform(temp, result_digit), run_time=0.3)
                self.remove(temp)
                self.add(result_digit)
                result_digits_mobs.append(result_digit)

                self.play(d1_digit.animate.set_color(WHITE), run_time=0.2)

            # 处理剩余进位（多位）
            extra_col = len(str_num1) + idx
            while carry:
                digit = carry % 10
                x_pos = get_column_x(extra_col)
                carry_mob = Integer(digit, color=BLUE, font_size=32).move_to([x_pos, row_y, 0])
                self.play(FadeIn(carry_mob), run_time=0.3)
                result_digits_mobs.append(carry_mob)
                carry //= 10
                extra_col += 1

            # 排序并保存整行
            result_digits_mobs.sort(key=lambda m: m.get_center()[0])
            row_group = VGroup(*result_digits_mobs)
            partial_rows.append(row_group)
            partial_values.append(int(str_num1) * int(d2))  # 记录值

            self.play(digit_to_highlight.animate.set_color(WHITE), run_time=0.3)
            self.wait(0.3)

        # ------------------- 添加第二条横线（在部分积之后）-------------------
        if not partial_rows:
            raise ValueError("No partial products generated.")

        last_partial_row = partial_rows[-1]
        underline2 = Line(line_left, line_right).next_to(last_partial_row, DOWN, buff=0.3)
        self.play(Create(underline2))
        self.wait(0.5)

        # =================== 🔥 加法阶段开始：部分积相加 ===================
        addition_title = Text("现在我们将这些结果相加", font_size=24, color=YELLOW).next_to(underline2, DOWN, buff=0.5)
        self.play(Write(addition_title))
        self.wait(1)
        self.play(FadeOut(addition_title))

        # 所有要加的行复制一份用于加法（避免影响原动画）
        addend_rows = [row.copy() for row in partial_rows]
        total_sum = sum(partial_values)
        str_total = str(total_sum)
        num_cols = len(str_total)

        # 定义每一列的 x 坐标（右对齐）
        col_centers = {}
        for col_idx in range(num_cols):
            col_centers[col_idx] = get_column_x(col_idx)  # 右数第 col_idx 列

        # ------------------- 初始化加法变量 -------------------
        current_carry_text = None  # 显示上方的进位
        carry_digits = {}  # carry_digits[col] = Integer 表示该列进位标记
        final_result_digits = []

        # 加法结果 y 坐标
        result_y = underline2.get_bottom()[1] - 0.8 * (len(partial_rows) + 1)

        # 从右到左逐列相加
        for col_idx in range(num_cols):  # col_idx = 0 是个位
            x_pos = col_centers[col_idx]

            # === 高亮当前列 ===
            brace = BraceBetweenPoints(
                np.array([x_pos - 0.3, top_line.get_top()[1], 0]),
                np.array([x_pos + 0.3, last_partial_row.get_bottom()[1], 0]),
                direction=LEFT,
                buff=0
            ).set_color(RED)
            label = Text(f"第 {col_idx+1} 列", font_size=18, color=RED).next_to(brace, LEFT)
            self.play(Create(brace), Write(label), run_time=0.5)

            # 收集当前列的所有数字（从各 partial row 中找最接近 x_pos 的 digit）
            col_sum = 0
            addend_digits_in_col = []

            for row in addend_rows:
                # 找这一行中最靠近该列 x 的数字
                closest = min(row, key=lambda m: abs(m.get_center()[0] - x_pos))
                if abs(closest.get_center()[0] - x_pos) < self.digit_width * 0.8:
                    col_sum += closest.number
                    addend_digits_in_col.append(closest)

            # 获取上一位进位（如果有）
            incoming_carry = carry_digits.get(col_idx - 1, None)
            if incoming_carry is not None:
                carry_val = incoming_carry.number
                col_sum += carry_val
            else:
                carry_val = 0

            # 计算当前位结果和新进位
            final_digit = col_sum % 10
            new_carry = col_sum // 10

            # 显示新的进位（写在上方）
            if new_carry > 0 and col_idx < num_cols - 1:
                carry_x = col_centers[col_idx + 1]
                carry_mob = Integer(new_carry, color=RED, font_size=24).move_to(
                    np.array([carry_x, top_line.get_top()[1] + 0.5, 0])
                )
                if current_carry_text:
                    self.play(Transform(current_carry_text, carry_mob))
                else:
                    self.play(FadeIn(carry_mob))
                    current_carry_text = carry_mob
                carry_digits[col_idx] = carry_mob

            # 创建最终结果数字
            result_digit_mob = Integer(final_digit, color=GREEN, font_size=36).move_to(
                np.array([x_pos, result_y, 0])
            )
            self.play(
                *[d.animate.set_color(YELLOW) for d in addend_digits_in_col],
                run_time=0.4
            )
            self.play(FadeIn(result_digit_mob), run_time=0.6)
            self.play(
                *[d.animate.set_color(BLUE) for d in addend_digits_in_col],
                run_time=0.4
            )

            final_result_digits.append(result_digit_mob)

            # 清除当前列高亮
            self.play(FadeOut(brace), FadeOut(label), run_time=0.3)

        # 移除最后进位显示
        if current_carry_text:
            self.play(FadeOut(current_carry_text))

        # ------------------- 最终结果组合与框出 -------------------
        final_group = VGroup(*reversed(final_result_digits))  # 因为是从右往左生成的
        underline3 = Line(line_left, line_right).next_to(final_group, DOWN, buff=0.2)
        self.play(Create(underline3))
        self.wait(0.5)

        result_box = SurroundingRectangle(final_group, color=GREEN, buff=0.15, stroke_width=4)
        conclusion = Text("最终答案！", font_size=28, color=GREEN).next_to(final_group, DOWN, buff=0.5)

        self.play(Create(result_box), Write(conclusion))
        self.wait(2)

        final_value = num1 * num2
        str_final = str(final_value)
        final_digits = []

        final_y = underline2.get_bottom()[1] - 0.6
        for i, d in enumerate(str_final):
            col_idx = len(str_final) - 1 - i  # 右数第几列
            x_pos = get_column_x(col_idx)
            digit = Integer(int(d), color=GREEN, font_size=self.result_font_size).move_to(
                np.array([x_pos, final_y, 0])
            )
            final_digits.append(digit)

        final_group = VGroup(*final_digits)

        # 显示最终结果
        self.play(FadeIn(final_group, shift=DOWN * 0.5), run_time=0.8)

        # 框出答案
        result_box = SurroundingRectangle(
            final_group,
            color=GREEN,
            buff=0.15,
            stroke_width=3
        )
        self.play(Create(result_box), run_time=0.8)
        self.wait(2)


# =============== 新增：供外部调用的函数 ===============
def render_multiplication(num1: int, num2: int, output_dir: str = "outputs", quality: str = "low_quality"):
    """
    渲染竖式乘法动画并返回视频文件路径。
    
    参数:
        num1 (int): 被乘数
        num2 (int): 乘数
        output_dir (str): 输出目录
        quality (str): 质量级别，必须是 Manim 支持的值，如 'low_quality', 'high_quality'
    
    返回:
        str: 生成的 MP4 文件绝对路径
    """
    # 设置配置
    config.preview = False
    config.quality = quality  # ✅ 使用合法值
    config.media_dir = output_dir
    config.video_dir = output_dir
    
    # 构造唯一文件名（避免冲突）
    filename = f"mult_{num1}x{num2}_{abs(hash((num1, num2))) % 10000}.mp4"
    config.output_file = filename

    # 渲染场景
    scene = VerticalMultiplicationWithAddition(num1=num1, num2=num2)
    scene.render()

    return os.path.abspath(os.path.join(output_dir, filename))


# =============== 主程序入口（保留命令行功能）===============
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Animate full vertical multiplication with addition and carry.")
    parser.add_argument("--num1", type=int, default=123, help="First number")
    parser.add_argument("--num2", type=int, default=45, help="Second number")
    parser.add_argument("--preview", action="store_true", help="Preview after render")
    parser.add_argument("--high_quality", action="store_true", help="Use high quality")
    parser.add_argument("--output_dir", type=str, default=None, help="Custom output directory")

    args = parser.parse_args()

    # ✅ 修复：使用合法的质量名称
    config.preview = args.preview
    config.quality = "high_quality" if args.high_quality else "low_quality"
    config.output_file = f"full_mult_{args.num1}x{args.num2}.mp4"
    if args.output_dir:
        config.media_dir = args.output_dir

    print(f"\n🎬 Rendering {args.num1} × {args.num2} with FULL process...")
    print(f"   Quality: {'High' if args.high_quality else 'Low'}")
    print(f"   Output: {config.output_file}")

    scene = VerticalMultiplicationWithAddition(num1=args.num1, num2=args.num2)
    scene.render()

    print("✅ Full animation completed!")