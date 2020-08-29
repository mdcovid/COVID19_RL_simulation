import numpy as np

import os
import sys
import yaml
import json
import itertools

from io import BytesIO
import base64

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def final_score(rewards):
    cumulated_score = sum(rewards)
    return cumulated_score

# def save_figures():
    # fig_list = list()
    # for i in plt.get_fignums():
        # plt.figure(i)
        # figfile = BytesIO()
        # # fig.set_size_inches(12)
        # plt.savefig(figfile, format='png')  # ,dpi=100)
        # figfile.seek(0)
        # fig_list.append(base64.b64encode(figfile.getvalue()).decode('ascii'))
    # return fig_list


# def html_text(fig_list):
    # html = """<html><head></head><body>\n"""
    # for i,figure in enumerate(fig_list):
        # if i %4==0 :
            # html+= "<hr> scenario {}<br>".format(i//4)
        # html += '<img src="data:image/png;base64,{0}"><br>'.format(figure)

    # html += """</body></html>"""

    # return html



def main():
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    print(input_dir)
    print(output_dir)

    submit_dir = os.path.join(input_dir, 'res')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(os.path.abspath(os.path.join(input_dir, 'log_file.json')), 'r') as file:
        file = json.load(file)
        score = final_score(file)
        print("Score on the leaderboard:", score)

        try:
            metadata = yaml.load(open(os.path.join(submit_dir, 'metadata'), 'r'))
            duration = metadata['elapsedTime']
        except:
            duration = 0

        output_filename = os.path.join(output_dir, 'scores.txt')
        with open(output_filename, 'w') as f:
            f.write("score: {}\n".format(score))
            f.write("Duration: %0.6f\n" % duration)
            f.close()

        # figure_list = save_figures()
        # output_filename = os.path.join(output_dir, 'scores.html')
        # with open(output_filename, 'w') as f:

            # # f.write("score: {}\n".format(score))
            # # f.write("plots incoming")
            # f.write(html_text(figure_list))
            # f.close()
        # # print("step : {}, cumulative rewards : {}".format(step,cumulative_reward ))
        
if __name__ == "__main__":
    main()
