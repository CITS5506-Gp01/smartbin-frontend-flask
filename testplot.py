import matplotlib.pyplot as plt
import numpy as np
import mpld3

fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.plot([1, 2, 3, 4], [1, 4, 2, 3])  # Plot some data on the axes.
print("done")
html_str = mpld3.fig_to_html(fig)

Html_file= open("test.html","w")
Html_file.write(html_str)
Html_file.close()