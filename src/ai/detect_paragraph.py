import easyocr
import matplotlib.pyplot as plt
from PIL import ImageDraw, Image

from src.ai.util import pil_cv2_convert
from src.ai.util import union_find

def detect_paragraph(image: Image.Image, merge: bool=True) -> list[(int, int, int, int)]:
    reader = easyocr.Reader(['ja'])
    ract, free = reader.detect(pil_cv2_convert.pil2cv(image), slope_ths=0.5, canvas_size=500000)
    ract = ract[0]
    free = free[0]

    for a, b, c, d in free:
        x1, y1 = a
        x2, y2 = b
        x3, y3 = c
        x4, y4 = d

        xmin = min(x1, x2, x3, x4)
        xmax = max(x1, x2, x3, x4)
        ymin = min(y1, y2, y3, y4)
        ymax = max(y1, y2, y3, y4)

        ract.append([xmin, xmax, ymin, ymax])

    is_in = lambda xmin, xmax, ymin, ymax, px, py, thre=10: xmin-thre <= px <= xmax+thre and ymin-thre <= py <= ymax+thre
    gen_point = lambda xmin, xmax, ymin, ymax: [(x, y) for x in [xmin, xmax] for y in [ymin, ymax]]

    n = len(ract)
    uf = union_find.UnionFind(n)
    for i in range(n):
        for j in range(i+1, n):
            collision = False
            for jp in gen_point(*ract[j]):
                if is_in(*ract[i], *jp):
                    collision = True
                    break
            else:
                for ip in gen_point(*ract[i]):
                    if is_in(*ract[j], *ip):
                        collision = True
                        break
            
            if collision:
                uf.merge(j, i)

    temp = [None for _ in range(n)]
    for i in range(n):
        j = uf.find(i) if merge else i

        if not temp[j]:
            temp[j] = ract[i]
        else:
            temp[j][0] = min(temp[j][0], ract[i][0])
            temp[j][1] = max(temp[j][1], ract[i][1])
            temp[j][2] = min(temp[j][2], ract[i][2])
            temp[j][3] = max(temp[j][3], ract[i][3])

    temp = list(filter(None, temp))
    result = [ list(map(int, (xmin, ymin, xmax-xmin, ymax-ymin))) for xmin, xmax, ymin, ymax in temp ]
    return result
