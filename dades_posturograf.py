import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import os
from sklearn.metrics import r2_score
from funcions import quadrant_angle, quadrant_vector, canvi_quadrant

directory = '/home/pau/Desktop/Quart Curs/TFG/Dades/Fitxers_posturograf_IMU/Fitxers per entrenar'
for filename in os.listdir(directory):
    if filename[-1] == 't':
        reader = pd.read_csv(directory + "/" + filename, delimiter="\t", encoding="cp1252", skiprows=1, chunksize=1, header=None)

        df_dades = reader.get_chunk()

        #'Nº_test', 'Val_test',Rep_test', 'EstML_test', 'EstAP_test'
        roa = df_dades.iloc[:,16:21].values.tolist()
        roc = df_dades.iloc[:,21:26].values.tolist()
        rga = df_dades.iloc[:,26:31].values.tolist()
        rgc = df_dades.iloc[:,31:36].values.tolist()

        ##SOM VIS VEST
        result = df_dades.iloc[:,53:56].values.tolist()

        num_test = roa[0][0] + roc[0][0] + rga[0][0] + rgc[0][0]
        """
        print(roa)
        print(roc)
        print(rga)
        print(rgc)
        print(result)

        print("Total tests")
        print(num_test)
        """

        #Carregar dades

        ##Resultats
        reader = pd.read_csv(directory + "/" + filename, delimiter="\t", encoding="cp1252", skiprows=2, chunksize=num_test, index_col=False)
        df_resultats = reader.get_chunk()
        df_resultats['test'] = df_resultats['Prueba ROMBERG'] + df_resultats['Numero'].astype(str)

        ##Posicions
        reader = pd.read_csv(directory + "/" + filename, delimiter="\t", encoding="cp1252",skiprows=(17+int(num_test)), chunksize=1200, index_col=False)
        df_dades_postu_XY = reader.get_chunk()

        ##Forçes
        df_dades_postu_FxFy  = pd.read_csv(directory + "/" + filename, delimiter="\t", encoding="cp1252",skiprows=(17+int(num_test)+1+1200), index_col=False)

        #Càlcul paràmetres posturògraf

        params = {'Desplaç_total' : [], 'Angle_total' : [], 'Dispersio_ML' : [], 'Dispersio_AP' : [], 'Area_barrida' : []
         , 'V_mitjana' : [], 'Desplaç_ML' : [], 'Desplaç_AP' : [], 'Fmax_ML' : [], 'Fmax_AP' : []} 
        
        ##Desplaçament total
        llista_test = df_resultats['test'].tolist()
        punts_X = {}
        punts_Y = {}

        for item in llista_test:
            punts_X[item] = df_dades_postu_XY[item + "_X"].values.tolist()
            punts_Y[item] = df_dades_postu_XY[item+"_Y"].values.tolist()
            params['Desplaç_total'].append(np.sqrt((sum(punts_X[item])/len(punts_X[item]))**2 + (sum(punts_Y[item])/len(punts_Y[item]))**2))

        ##Angle total(º)
        #print(filename)
        for item in llista_test:
            vector_nuvp = [(sum(punts_X[item])/len(punts_X[item])),(sum(punts_Y[item])/len(punts_Y[item]))]
            #print(vector_nuvp)
            quadrant_to = quadrant_vector(vector_nuvp)
            #print("quadrant_to: ", quadrant_to)
            angle = math.degrees(math.atan(vector_nuvp[1]/vector_nuvp[0]))
            quadrant_from = quadrant_angle(angle)
            #print("quadrant_from: ", quadrant_from)
            
            params['Angle_total'].append(canvi_quadrant(angle, quadrant_from, quadrant_to))
        """
        print('Estimades')
        print(params['Angle_total'])
        print('Reals')
        print(df_resultats['Angulo Desplaz.(º)'])
        """
        ##Dispersio ML i AP
        for item in llista_test:
            centre_X = sum(punts_X[item])/(len(punts_X[item])-1)
            centre_Y = sum(punts_Y[item])/(len(punts_Y[item])-1)
            params['Dispersio_ML'].append(np.sqrt(sum([((x - centre_X) ** 2) for x in punts_X[item]]) / (len(punts_X[item])-1)))
            params['Dispersio_AP'].append(np.sqrt(sum([((y - centre_Y) ** 2) for y in punts_Y[item]]) / (len(punts_Y[item])-1)))

        ##Area barrida
        for item in llista_test:
            points = np.vstack((punts_X[item], punts_Y[item])).T
            dades_centrades = points - np.mean(points, axis=0)
            covariance_matrix = np.cov(dades_centrades, rowvar=False)
            eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
            params['Area_barrida'].append(np.sqrt(eigenvalues[0]*eigenvalues[1])*4)

        ##Velocitat mitjana
        for item in llista_test:
            points = np.vstack((punts_X[item], punts_Y[item])).T
            num_points = len(points)
            total_dist = 0.0

            for i in range(num_points - 1):
                total_dist += np.linalg.norm(points[i+1] - points[i])
                    
            params['V_mitjana'].append((total_dist/1000)/30)


        ##Desplaçament ML i AP
        for item in llista_test:
            params['Desplaç_ML'].append(np.max(punts_X[item]) - np.min(punts_X[item]))
            params['Desplaç_AP'].append(np.max(punts_Y[item]) - np.min(punts_Y[item]))

        ##Força màxima
        for item in llista_test:
            forca_X = df_dades_postu_FxFy[item + "_Fx"].values.tolist()
            forca_Y = df_dades_postu_FxFy[item+"_Fy"].values.tolist()
            params['Fmax_ML'].append(np.max(forca_X) - np.min(forca_X))
            params['Fmax_AP'].append(np.max(forca_Y) - np.min(forca_Y))

        #Comparació amb dades reals
        ##Calcular l'R²
        r2 = []

        r2.append(r2_score(df_resultats['Desplaz.Total(mm)'], params['Desplaç_total']))
        r2.append(r2_score(df_resultats['Angulo Desplaz.(º)'], params['Angle_total']))
        r2.append(r2_score(df_resultats['Dispers ML (mm)'], params['Dispersio_ML']))
        r2.append(r2_score(df_resultats['Dispers AP (mm)'], params['Dispersio_AP']))
        r2.append(r2_score(df_resultats['Area barrida (mm2)'], params['Area_barrida']))
        r2.append(r2_score(df_resultats['Velocidad media (m/s)'], params['V_mitjana']))
        r2.append(r2_score(df_resultats['Desplazam.ML (mm)'], params['Desplaç_ML']))
        r2.append(r2_score(df_resultats['Desplazam.AP(mm)'], params['Desplaç_AP']))
        r2.append(r2_score(df_resultats['Fuerza Max ML (N)'], params['Fmax_ML']))
        r2.append(r2_score(df_resultats['Fuerza Max AP (N)'], params['Fmax_AP']))

        #print("R^2 de cada paràmetre: ", r2)
        #print("R^2 mitjana: ", np.mean(r2))






