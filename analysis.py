import glob
import matplotlib
import numpy as np
import pandas as pd
import random
import re
import matplotlib.pyplot as plt
from adjustText import adjust_text
from nltk.stem.snowball import EnglishStemmer
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from wordcloud import WordCloud, ImageColorGenerator
from matplotlib import pyplot as plt
from PIL import Image

class StemmingTfidfVectorizer(TfidfVectorizer):
    def build_analyzer(self):
        stemmer = EnglishStemmer()
        analyzer = super(TfidfVectorizer, self).build_analyzer()
        return lambda doc: [stemmer.stem(word) for word in analyzer(doc)]

def grey_color(word, font_size, position, orientation, random_state=None, **kwargs):
    return 'hsl(0, 0%%, %d%%)' % random.randint(50, 100)

def generate_wordcloud(tfidf_scores, image, saveto='wordcloud.png'):
    coloring = np.array(Image.open(image))
    image_colors = ImageColorGenerator(coloring)
    wc = WordCloud(
            max_words=500,
            mask=coloring,
            max_font_size=40,
            random_state=42,
            background_color = '#1A1A25',
            color_func=grey_color,
            collocations=False,
            font_path='~/Library/Fonts/HelveticaNeueLT/HelveticaNeueLT-BoldCond.otf',
            relative_scaling=0.8)

    wc.generate_from_frequencies(tfidf_scores)
    wc.to_file(saveto)
    return wc

def main():
    pattern = './data/corpus_large/*'
    documents = glob.glob(pattern)
    vectorizer = StemmingTfidfVectorizer(input='filename', max_df=.5, min_df=1, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    terms = vectorizer.get_feature_names()

    #most popular terms
    maxmatrix = np.argmax(tfidf_matrix.toarray(), axis=1)
    for index, document in enumerate(documents):
        print("{}: {}".format(document, terms[maxmatrix[index]]))

    #clustering
    kmeans = KMeans(n_clusters=5, random_state=0, n_init=20)
    for document, cluster in zip(documents, kmeans.fit_predict(tfidf_matrix)):
        print("{}: {}".format(document, cluster))

    #cosine similarity
    similarity = cosine_similarity(tfidf_matrix)
    for index, file in enumerate(documents):
        print("{}: {}".format(file, (list(similarity[index]))))

    #t-SNE
    tsne = TSNE(n_components=2,
                random_state=0,
                n_iter=10000,
                metric='cosine',
                learning_rate=1,
                perplexity=5)
    dense_tfidf_matrix = tfidf_matrix.todense()
    points_tsne = tsne.fit_transform(dense_tfidf_matrix)

    #PCA
    sklearn_pca = PCA(n_components=2)
    points_pca = sklearn_pca.fit_transform(dense_tfidf_matrix)

    #visualization 
    matplotlib.style.use('ggplot')
    df = pd.DataFrame(points_tsne, index=documents, columns=['x', 'y'])
    fig, ax = plt.subplots()
    df.plot('x', 'y', kind='scatter', ax=ax, alpha=0)
    texts = []
    for k, v in df.iterrows():
        texts.append(plt.text(v[0], v[1], re.search(r'-(.*?)\.', k).group(1)))
    adjust_text(texts)
    plt.axis('off')
    plt.show()

if __name__ == '__main__':
    main()
