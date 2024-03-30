import torch
from tqdm import tqdm
from utils import *


class ModelRandom(object):
    '''
    Model class
    The train computes the loss based on a percent of randomly chosen nodes
    '''

    def __init__(self, lr, maxIters):
        self.lr = lr
        self.maxIters = maxIters
        self.optimizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def set_Adam_optimizer(self, pos):
        self.optimizer = torch.optim.Adam([pos], self.lr)

    def train(self, graph, percentage, save_path):
        graph.init_postions()


        self.set_Adam_optimizer(graph.pos)
        losses = []

        # first step
        for i in tqdm(range(self.maxIters)):
            self.optimizer.zero_grad()
            l = stress(graph)
            l.backward()
            self.optimizer.step()
            losses.append(l.item())

        # Step: computes a random subset (based on percentage) of nodes and colors them red
        node_dic = nodeColoring(graph.G, percentage)

        for node in graph.G.nodes:
            graph.G.nodes[node]['color'] = node_dic[node]
        count_colors(len(graph.G.nodes), self.device, graph.G)

        # FIGURE: Gamma_0 - Min Stress
        save_graph(graph, node_dic=node_dic, title="gamma0", save_path=save_path)

        # Second step
        stress_min = l.item()
        unfair_stress_min = unfairness(graph).item()

        first_cut = 5
        threshold_five = stress_min * (1 + first_cut / 100)

        second_cut = 20
        threshold_twenty = stress_min * (1 + second_cut / 100)

        currentStress = stress_min
        is_five_saved = False

        self.set_Adam_optimizer(graph.pos)
        losses = []
        i = 0
        pbar = tqdm(total=self.maxIters)

        # Unfairness Minimization
        while i < self.maxIters and currentStress < threshold_twenty:

            if currentStress >= threshold_five and not is_five_saved:
                stress_5 = currentStress
                unfair_5 = l = unfairness(graph).item()
                is_five_saved = True

                # FIGURE 2: Gamma_1 - 5 Percent Worse
                save_graph(graph, node_dic=node_dic, title=f'gamm1', save_path=save_path)
                plt.show()

            self.optimizer.zero_grad()
            l = unfairness(graph)
            l.backward()
            self.optimizer.step()

            losses.append(l.item())
            currentStress = stress(graph).item()
            i += 1
            pbar.update(1)

        pbar.close()

        # FIGURE: Gamma_2 - 20 percent worse
        save_graph(graph, node_dic=node_dic, title=f'gamma2', save_path=save_path)

        stress_20 = stress(graph).item()
        unfair_20 = unfairness(graph).item()

        # If the threshold remains below 5% => only one figure 5=20=final
        if not is_five_saved:
            stress_5 = stress_20
            unfair_5 = unfair_20

        return stress_min, unfair_stress_min, stress_5, unfair_5, stress_20, unfair_20


class ModelMostStress(object):
    '''
    Model class
    The train computes the loss based on the most stressed nodes
    '''


    def __init__(self, lr, maxIters):
        self.lr = lr
        self.maxIters = maxIters
        self.optimizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def set_Adam_optimizer(self, pos):
        self.optimizer = torch.optim.Adam([pos], self.lr)

    def train(self, graph, save_path):
        graph.init_postions()

        self.set_Adam_optimizer(graph.pos)
        losses = []

        # first step
        for i in tqdm(range(self.maxIters)):
            self.optimizer.zero_grad()
            l = stress(graph)
            l.backward()
            self.optimizer.step()
            losses.append(l.item())

        # Step: computes the most stressed nodes and colors them
        percentage = 10
        node_dic = nodeColoring_stress(graph.G, percentage, graph.pos, graph.D, graph.W)
        for node in graph.G.nodes:
            graph.G.nodes[node]['color'] = node_dic[node]
        count_colors(len(graph.G.nodes), self.device, graph.G)

        # FIGURE: Gamma_0 - Min Stress
        save_graph(graph, node_dic=node_dic, title="gamma0", save_path=save_path)

        # Second step
        stress_min = l.item()
        unfair_stress_min = unfairness(graph).item()

        first_cut = 5
        threshold_five = stress_min * (1 + first_cut / 100)

        second_cut = 20
        threshold_twenty = stress_min * (1 + second_cut / 100)

        currentStress = stress_min
        is_five_saved = False

        self.set_Adam_optimizer(graph.pos)
        losses = []
        i = 0
        pbar = tqdm(total=self.maxIters)

        # Unfairness Minimization
        while i < self.maxIters and currentStress < threshold_twenty:

            if currentStress >= threshold_five and not is_five_saved:
                stress_5 = currentStress
                unfair_5 = l = unfairness(graph).item()
                is_five_saved = True

                # FIGURE 2: Gamma_1 - 5 Percent Worse
                save_graph(graph, node_dic=node_dic, title=f'gamma1', save_path=save_path)
                plt.show()

            self.optimizer.zero_grad()
            l = unfairness(graph)
            l.backward()
            self.optimizer.step()

            losses.append(l.item())
            currentStress = stress(graph).item()
            i += 1
            pbar.update(1)

        pbar.close()

        # FIGURE: Gamma_2 - 20 percent worse
        save_graph(graph, node_dic=node_dic, title=f'gamma2', save_path=save_path)

        stress_20 = stress(graph).item()
        unfair_20 = unfairness(graph).item()

        # If the threshold remains below 5% => only one figure 5=20=final
        if not is_five_saved:
            stress_5 = stress_20
            unfair_5 = unfair_20

        return stress_min, unfair_stress_min, stress_5, unfair_5, stress_20, unfair_20
