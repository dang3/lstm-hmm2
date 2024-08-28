import matplotlib.pyplot as plt
import numpy as np

X = np.array([5,10,15,20])
LABELS = ['5', '10', '15', '20']
baseline = [83.56, 57.50, 51.22, 50.48]
no_embedding = [55.73, 39.28, 34.47, 30.55]
with_embedding = [74.66, 54.89, 53.36, 49.66]
bidirectional = [89.66, 79.30, 75.50, 73.36]
bidirectional_cnn = [94.32, 87.38, 86.91, 81.06]

offset_amt = 0.45
axes_label_font_size = 15

plt.figure(figsize=(15,8))
bars1 = plt.bar(X - 4*offset_amt, no_embedding, color='darkred', label="No embedding") 
bars2 = plt.bar(X - 2*offset_amt, with_embedding, color='darkorange', label="With embedding")   
bars3 = plt.bar(X, baseline, color='khaki', label="MLP Only")  
bars4 = plt.bar(X + 2*offset_amt, bidirectional, color='dodgerblue', label="With embedding and biLSTM") 
bars5 = plt.bar(X + 4*offset_amt, bidirectional_cnn, color='forestgreen', label="With embedding, biLSTM and CNN") 

all_bars = [bars1, bars2, bars3, bars4, bars5]

for bars in all_bars:
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x(), yval + 1, yval, fontsize=12)

axes = plt.gca()
axes.set_ylim([0,110])

plt.xticks(X, LABELS)
plt.xlabel("Number of Families to Classify", fontsize=axes_label_font_size)
plt.ylabel("Average Accuracy (%)", fontsize=axes_label_font_size)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend()
plt.title("Average Evaluation Accuracy Over 5 Experimental Runs of Each \nModel For Varying Number of Unique Families to Classify", 
            fontsize=axes_label_font_size+5,
            weight="bold")



plt.show()

