"""
Fitxer on es carreguen en un fitxer .csv els valors de l'acceleració màxima, 
el màxim del vector gravetat i el màxim desplaçament de cada pacient del
arxiu Mataro_postu_IMU. 
"""
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize
import numpy as np
from AHRS import AHRS
from quaternions import quaternRotate
import pandas as pd
from funcions import convertData, convertDataHex, grafica, find_discontinuity, obtenir_x_valors

txt = [] 
csv = []
scores = [] #Llista amb les valoracions de cada prova
"""
Llistes amb sis subllistes a dins(una per cada edat dels 68 als 73 anys) 
i 4 subllistes a dins de cada una(una per cada test).
"""

directory = "C:/Users/Usuario/OneDrive/Escritorio/Universitat/TFG/Mataro_postu_IMU"

for i in range(6):
    txt.append([])
    csv.append([])
    scores.append([])
    
for filename in os.listdir(directory):
     if filename.endswith(".txt"): 
        underscore_index = filename.rfind("_")
        dot_index = filename.rfind(".")
        codi = filename[underscore_index+1:dot_index]
        
        reader = pd.read_csv(directory + filename, delimiter="\t", encoding="ansi", skiprows=1, chunksize=1, header=None)
        df_dades = reader.get_chunk()
        
        txt[df_dades[9].item()-68].append(directory + filename)
        scores[df_dades[9].item()-68].append(df_dades[[17]].values[0][0])
        scores[df_dades[9].item()-68].append(df_dades[[22]].values[0][0])
        scores[df_dades[9].item()-68].append(df_dades[[27]].values[0][0])
        scores[df_dades[9].item()-68].append(df_dades[[32]].values[0][0])
        
        for filename2 in os.listdir(directory):
            if filename2.endswith(".csv"):       
                if codi.lower() in filename2.lower():
                    csv[df_dades[9].item()-68].append(directory + filename2)    

scores = scores[0] + scores[1] + scores[2] + scores[3] + scores[4] + scores[5] 

valors_acc = []
valors_grav = []
valors_quat = []

dades_quat_raw = []
dades_acc_raw = []
dades_grav_raw = []
edat = []
prova = []
tag = []

deltat = 1/40

for i in range(6):
    valors_acc.append([])
    valors_grav.append([])
    valors_quat.append([])

for i in range(len(valors_acc)):
    for j in range(4):
        valors_acc[i].append([])
        valors_grav[i].append([])
        valors_quat[i].append([])
        
#print(valors_acc)
#print(valors_grav)

for index, rang in enumerate(csv):
    for file in rang:
        edat.append(68 + index)
        edat.append(68 + index)
        edat.append(68 + index)
        edat.append(68 + index)
        barra_index = file.rfind("/")        
        tag.append(file[barra_index+4:barra_index+9])
        tag.append(file[barra_index+4:barra_index+9])
        tag.append(file[barra_index+4:barra_index+9])
        tag.append(file[barra_index+4:barra_index+9])
        dades = pd.read_csv(file, delimiter=";")
        convertData(dades,"accelerometerY",10)
        convertData(dades,"accelerometerZ",10)
        convertData(dades,"accelerometerX",10)        
        convertDataHex(dades,"gravityVectorY",10)
        convertDataHex(dades,"gravityVectorZ",10)
        convertDataHex(dades,"gravityVectorX",10)
        convertDataHex(dades,"gyroscopeX",10)
        convertDataHex(dades,"gyroscopeY",10)
        convertDataHex(dades,"gyroscopeZ",10) 
                
        balance_test = dades.loc[dades["test"]==5, ["action","accelerometerX","accelerometerY","accelerometerZ", "gravityVectorY", "gravityVectorZ", "gyroscopeX", "gyroscopeY", "gyroscopeZ"]]
        llista_ROA = balance_test.index[balance_test["action"] == 1].tolist()
        llista_ROC = balance_test.index[balance_test["action"] == 2].tolist()
        llista_RGA = balance_test.index[balance_test["action"] == 3].tolist()
        llista_RGC = balance_test.index[balance_test["action"] == 4].tolist()
        balance_test.drop("action", inplace=True, axis=1)       
        
        prova.append("ROA")
        prova.append("ROC")        
        prova.append("RGA")        
        prova.append("RGC")        
        
        if len(llista_ROA) > 1:
            ind, missing_value = find_discontinuity(llista_ROA)
            ROA1 = [*range(llista_ROA[0], missing_value)]

            resultat=grafica(ROA1)
            
            rotated_vector = np.array([1.0,0.0,0.0])
            trajectoriax = [rotated_vector[0]]
            trajectoriay = [rotated_vector[1]]
            trajectoriaz = [rotated_vector[2]]
            
            AHRSalgorithm = AHRS(SamplePeriod=1/40, Kp=1,Ki=1, KpInit=1)

            for i in range(len(resultat[0])):
                AHRSalgorithm.Kp = 0
                AHRSalgorithm.UpdateIMU(resultat[0][['gyroscopeX', 'gyroscopeY', 'gyroscopeZ']].iloc[i].values.tolist(), 
                                        resultat[0][['accelerometerX', 'accelerometerX', 'accelerometerX']].iloc[i].values.tolist())
                quaternions = AHRSalgorithm.Quaternion
                rotated_vector = quaternRotate(rotated_vector, quaternions)
                trajectoriax.append(trajectoriax[-1] + rotated_vector[0]*deltat)
                trajectoriay.append(trajectoriay[-1] + rotated_vector[1]*deltat)
                trajectoriaz.append(trajectoriaz[-1] + rotated_vector[2]*deltat)
                
            valors_quat[index][0].append([max(trajectoriaz) - min(trajectoriaz), max(trajectoriay) - min(trajectoriay)])
            
            dades_quat_raw.append([max(trajectoriaz) - min(trajectoriaz), max(trajectoriay) - min(trajectoriay)])
            
            valors_acc[index][0].append([max(normalize([resultat[0]["accelerometerZ"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerZ"]*9.81])[0]),
                                  max(normalize([resultat[0]["accelerometerY"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerY"]*9.81])[0])]) 

            valors_grav[index][0].append([max(normalize([resultat[0]["gravityVectorZ"]])[0]) - min(normalize([resultat[0]["gravityVectorZ"]])[0]),
                                   max(normalize([resultat[0]["gravityVectorY"]])[0]) - min(normalize([resultat[0]["gravityVectorY"]])[0])]) 
            
            dades_acc_raw.append([max(normalize([resultat[0]["accelerometerZ"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerZ"]*9.81])[0]),
                                  max(normalize([resultat[0]["accelerometerY"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerY"]*9.81])[0])])
            
            dades_grav_raw.append([max(normalize([resultat[0]["gravityVectorZ"]])[0]) - min(normalize([resultat[0]["gravityVectorZ"]])[0]),
                                   max(normalize([resultat[0]["gravityVectorY"]])[0]) - min(normalize([resultat[0]["gravityVectorY"]])[0])])  
        else:
            valors_quat[index][0].append([2,2])
            valors_acc[index][0].append([2,2])
            valors_grav[index][0].append([2,2])
            dades_acc_raw.append([2,2])
            dades_grav_raw.append([2,2])
            dades_quat_raw.append([2,2])
            
            print("El fitxer ", file, " ", "no té prova ROA")
            
        if len(llista_ROC) > 1:
            ind, missing_value = find_discontinuity(llista_ROC)
            ROC1 = [*range(llista_ROC[0], missing_value)]

            resultat=grafica(ROC1)
            
            rotated_vector = np.array([1.0,0.0,0.0])
            trajectoriax = [rotated_vector[0]]
            trajectoriay = [rotated_vector[1]]
            trajectoriaz = [rotated_vector[2]]
            
            AHRSalgorithm = AHRS(SamplePeriod=1/40, Kp=1,Ki=1, KpInit=1)

            for i in range(len(resultat[0])):
                AHRSalgorithm.Kp = 0
                AHRSalgorithm.UpdateIMU(resultat[0][['gyroscopeX', 'gyroscopeY', 'gyroscopeZ']].iloc[i].values.tolist(), 
                                        resultat[0][['accelerometerX', 'accelerometerX', 'accelerometerX']].iloc[i].values.tolist())
                quaternions = AHRSalgorithm.Quaternion
                rotated_vector = quaternRotate(rotated_vector, quaternions)
                #print(rotated_vector)
                trajectoriax.append(trajectoriax[-1] + rotated_vector[0]*deltat)
                trajectoriay.append(trajectoriay[-1] + rotated_vector[1]*deltat)
                trajectoriaz.append(trajectoriaz[-1] + rotated_vector[2]*deltat)
            
            valors_quat[index][1].append([max(trajectoriaz) - min(trajectoriaz), max(trajectoriay) - min(trajectoriay)])
            
            dades_quat_raw.append([max(trajectoriaz) - min(trajectoriaz), max(trajectoriay) - min(trajectoriay)])            
            
            valors_acc[index][1].append([max(normalize([resultat[0]["accelerometerZ"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerZ"]*9.81])[0]),
                                  max(normalize([resultat[0]["accelerometerY"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerY"]*9.81])[0])]) 

            valors_grav[index][1].append([max(normalize([resultat[0]["gravityVectorZ"]])[0]) - min(normalize([resultat[0]["gravityVectorZ"]])[0]),
                                   max(normalize([resultat[0]["gravityVectorY"]])[0]) - min(normalize([resultat[0]["gravityVectorY"]])[0])]) 


            dades_acc_raw.append([max(normalize([resultat[0]["accelerometerZ"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerZ"]*9.81])[0]),
                                  max(normalize([resultat[0]["accelerometerY"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerY"]*9.81])[0])])
            
            dades_grav_raw.append([max(normalize([resultat[0]["gravityVectorZ"]])[0]) - min(normalize([resultat[0]["gravityVectorZ"]])[0]),
                                   max(normalize([resultat[0]["gravityVectorY"]])[0]) - min(normalize([resultat[0]["gravityVectorY"]])[0])])
        else:
            valors_quat[index][0].append([2,2])
            valors_acc[index][1].append([2,2])
            valors_grav[index][1].append([2,2])
            dades_acc_raw.append([2,2])
            dades_grav_raw.append([2,2])
            dades_quat_raw.append([2,2])
            print("El fitxer ", file, " ", "no té prova ROC")
        
        if len(llista_RGA) > 1:        
            ind, missing_value = find_discontinuity(llista_RGA)
            RGA1 = [*range(llista_RGA[0], missing_value)]

            resultat=grafica(RGA1)
            
            rotated_vector = np.array([1.0,0.0,0.0])
            trajectoriax = [rotated_vector[0]]
            trajectoriay = [rotated_vector[1]]
            trajectoriaz = [rotated_vector[2]]
            
            AHRSalgorithm = AHRS(SamplePeriod=1/40, Kp=1,Ki=1, KpInit=1)

            for i in range(len(resultat[0])):
                AHRSalgorithm.Kp = 0
                AHRSalgorithm.UpdateIMU(resultat[0][['gyroscopeX', 'gyroscopeY', 'gyroscopeZ']].iloc[i].values.tolist(), 
                                        resultat[0][['accelerometerX', 'accelerometerX', 'accelerometerX']].iloc[i].values.tolist())
                quaternions = AHRSalgorithm.Quaternion
                rotated_vector = quaternRotate(rotated_vector, quaternions)
                #print(rotated_vector)
                trajectoriax.append(trajectoriax[-1] + rotated_vector[0]*deltat)
                trajectoriay.append(trajectoriay[-1] + rotated_vector[1]*deltat)
                trajectoriaz.append(trajectoriaz[-1] + rotated_vector[2]*deltat)
            
            valors_quat[index][2].append([max(trajectoriaz) - min(trajectoriaz), max(trajectoriay) - min(trajectoriay)])
            
            dades_quat_raw.append([max(trajectoriaz) - min(trajectoriaz), max(trajectoriay) - min(trajectoriay)])
            
            valors_acc[index][2].append([max(normalize([resultat[0]["accelerometerZ"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerZ"]*9.81])[0]),
                                  max(normalize([resultat[0]["accelerometerY"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerY"]*9.81])[0])]) 

            valors_grav[index][2].append([max(normalize([resultat[0]["gravityVectorZ"]])[0]) - min(normalize([resultat[0]["gravityVectorZ"]])[0]),
                                   max(normalize([resultat[0]["gravityVectorY"]])[0]) - min(normalize([resultat[0]["gravityVectorY"]])[0])]) 

            
            dades_acc_raw.append([max(normalize([resultat[0]["accelerometerZ"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerZ"]*9.81])[0]),
                                  max(normalize([resultat[0]["accelerometerY"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerY"]*9.81])[0])])
            
            dades_grav_raw.append([max(normalize([resultat[0]["gravityVectorZ"]])[0]) - min(normalize([resultat[0]["gravityVectorZ"]])[0]),
                                   max(normalize([resultat[0]["gravityVectorY"]])[0]) - min(normalize([resultat[0]["gravityVectorY"]])[0])])
        else:
            valors_quat[index][0].append([2,2])
            valors_acc[index][2].append([2,2])
            valors_grav[index][2].append([2,2])
            dades_acc_raw.append([2,2])
            dades_grav_raw.append([2,2])
            dades_quat_raw.append([2,2])
            print("El fitxer ", file, " ", "no té prova RGA")

        if len(llista_RGC) > 1:
            ind, missing_value = find_discontinuity(llista_RGC)
            RGC1 = [*range(llista_RGC[0], missing_value)]

            resultat=grafica(RGC1)
            
            rotated_vector = np.array([1.0,0.0,0.0])
            trajectoriax = [rotated_vector[0]]
            trajectoriay = [rotated_vector[1]]
            trajectoriaz = [rotated_vector[2]]
            
            AHRSalgorithm = AHRS(SamplePeriod=1/40, Kp=1,Ki=1, KpInit=1)

            for i in range(len(resultat[0])):
                AHRSalgorithm.Kp = 0
                AHRSalgorithm.UpdateIMU(resultat[0][['gyroscopeX', 'gyroscopeY', 'gyroscopeZ']].iloc[i].values.tolist(), 
                                        resultat[0][['accelerometerX', 'accelerometerX', 'accelerometerX']].iloc[i].values.tolist())
                quaternions = AHRSalgorithm.Quaternion
                rotated_vector = quaternRotate(rotated_vector, quaternions)
                #print(rotated_vector)
                trajectoriax.append(trajectoriax[-1] + rotated_vector[0]*deltat)
                trajectoriay.append(trajectoriay[-1] + rotated_vector[1]*deltat)
                trajectoriaz.append(trajectoriaz[-1] + rotated_vector[2]*deltat)
            
            valors_quat[index][3].append([max(trajectoriaz) - min(trajectoriaz), max(trajectoriay) - min(trajectoriay)])
            
            dades_quat_raw.append([max(trajectoriaz) - min(trajectoriaz), max(trajectoriay) - min(trajectoriay)])
            
            valors_acc[index][3].append([max(normalize([resultat[0]["accelerometerZ"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerZ"]*9.81])[0]),
                                  max(normalize([resultat[0]["accelerometerY"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerY"]*9.81])[0])]) 

            valors_grav[index][3].append([max(normalize([resultat[0]["gravityVectorZ"]])[0]) - min(normalize([resultat[0]["gravityVectorZ"]])[0]),
                                   max(normalize([resultat[0]["gravityVectorY"]])[0]) - min(normalize([resultat[0]["gravityVectorY"]])[0])]) 
            
            dades_acc_raw.append([max(normalize([resultat[0]["accelerometerZ"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerZ"]*9.81])[0]),
                                  max(normalize([resultat[0]["accelerometerY"]*9.81])[0]) - min(normalize([resultat[0]["accelerometerY"]*9.81])[0])])
            
            dades_grav_raw.append([max(normalize([resultat[0]["gravityVectorZ"]])[0]) - min(normalize([resultat[0]["gravityVectorZ"]])[0]),
                                   max(normalize([resultat[0]["gravityVectorY"]])[0]) - min(normalize([resultat[0]["gravityVectorY"]])[0])])
        else:
            valors_quat[index][0].append([2,2])
            valors_acc[index][3].append([2,2])
            valors_grav[index][3].append([2,2])
            dades_acc_raw.append([2,2])
            dades_grav_raw.append([2,2])
            dades_quat_raw.append([2,2])
            print("El fitxer ", file, " ", "no té prova RGC")           

dades = {'Forca_maxima_acc_x': obtenir_x_valors(dades_acc_raw, 0), 'Forca_maxima_acc_y': obtenir_x_valors(dades_acc_raw, 1) ,
         'Forca_maxima_grav_x': obtenir_x_valors(dades_grav_raw, 0), 'Forca_maxima_grav_y': obtenir_x_valors(dades_grav_raw, 1),
         'Desplacament_maxim_x': obtenir_x_valors(dades_quat_raw, 0), 'Desplacament_maxim_y': obtenir_x_valors(dades_quat_raw, 1),
         'Prova': prova, 'Puntuacio': scores, 'Edat': edat, 'Etiqueta': tag}
df = pd.DataFrame(data=dades)
df = df.replace('-', 0)

df.to_csv('../dades_força_IMU.csv')

