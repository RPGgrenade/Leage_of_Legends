import csv

def make_csv(output_name, dictionary):
    with open(output_name + '.csv', 'w') as f:
        w = csv.writer(f)
        for key,value in dictionary.items():

            support = value.get('SUPPORT', 0)
            duo_support = value.get('DUO_SUPPORT',0)
            none = value.get('NONE',0)
            solo = value.get('SOLO',0)
            duo = value.get('DUO',0)
            duo_carry = value.get('DUO_CARRY',0)
            top = value.get('TOP',0)
            middle = value.get('MIDDLE',0)
            jungle = value.get('JUNGLE',0)
            bottom = value.get('BOTTOM',0)

            w.writerow([key,
                        support,
                        duo_support,
                        none,
                        solo,
                        duo,
                        duo_carry,
                        top,
                        middle,
                        jungle,
                        bottom])