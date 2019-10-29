from flask import Flask, redirect, request, render_template, send_from_directory
from PIL import Image
import numpy as np, math, os, string, random

app = Flask(__name__)

SAVE_DIR = "./images"
if not os.path.isdir(SAVE_DIR):
    os.mkdir(SAVE_DIR)

app = Flask(__name__, static_url_path="")


def random_str(n):
    return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])


@app.route('/')
def index():
    return render_template('index.html', images=os.listdir(SAVE_DIR)[::-1])


@app.route('/images/<path:path>')
def send_js(path):
    return send_from_directory(SAVE_DIR, path)


@app.route('/upload', methods=['POST'])
def upload():
    if request.files['image']:
        print(request.form['width'], request.form['height'], request.form['rotation'])

        # if not request.form['width'].isdigit() or not request.form['height'].isdigit() or not request.form['rotation'].isdigit():
        #     return redirect('/')
        v_x, v_y, v_r = float(request.form['width']), float(request.form['height']), float(request.form['rotation'])
        rotate = math.radians(v_r)

        # 画像として読み込み
        pic = np.array(Image.open(request.files['image'].stream))
        pic_h, pic_w, _ = pic.shape
        # img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)
        # img = cv2.imdecode(img_array, 1)

        changed_w = int(pic_w * v_x)
        changed_h = int(pic_h * v_y)

        out_pic = Image.new('RGB', (changed_w, changed_h))

        for i in range(changed_h):
            y = changed_h / 2 - i
            for j in range(changed_w):
                x = changed_w / 2 - j
                # 新しい画像が参考にする元の画素が整数かどうかを確かめ、整数でなかった場合はその差をとる

                # 参考にする画素を4つの画素を左上から順にS1,S2,S3,S4とおく

                new_x = (x * np.cos(rotate) - y * np.sin(rotate) + changed_h / 2) / v_x
                new_round_x = int(new_x)
                dx = new_x - new_round_x

                new_y = ((y * np.cos(rotate) + x * np.sin(rotate)) + changed_w / 2) / v_y
                new_round_y = int(new_y)
                dy = new_y - new_round_y

                # print(dx, dy)

                # v_x, y = pic[(1 - dx) * (1 - dy)]

                # print(after_i, after_j)
                # print(i,j)
                # print(pic[after_i, after_j])

                # (new_round_x,new_round_y)がS1の画素値を表す
                # print(pic[new_round_y, new_round_x])

                # 拡大縮小後の画素に拡大縮小前の画素値を代入する

                # RGBの画素値を足し合わせるために使う

                if 0 < new_round_x + 1 < pic_w and 0 < new_round_y + 1 < pic_h:
                    r = pic[new_round_y, new_round_x] * (1 - dx) * (1 - dy) + pic[new_round_y, new_round_x + 1] * dx * (
                            1 - dy) + pic[new_round_y + 1, new_round_x] * (1 - dx) * dy + pic[
                            new_round_y + 1, new_round_x + 1] * dx * dy

                    a, b, c = r
                    out_pic.putpixel((j, i), (int(a), int(b), int(c)))

        # 保存
        # dt_now = datetime.now().strftime("%Y_%m_%d%_H_%M_%S_") + random_str(5)

        randlst = "".join([random.choice(string.ascii_letters + string.digits) for i in range(10)])

        save_path = os.path.join(SAVE_DIR, randlst + ".png")
        out_pic.save(save_path , quality=95)
        print("save", save_path)

        return redirect('/')


if __name__ == '__main__':
    app.run()
