
def check_rivers(riv, M, H):
    river_status =''
    for n in range(len(riv.riverno)):

        i = int(riv.xpos[n])
        j = int(riv.ypos[n])

        if riv.direction[n] == 0: # U point
            if riv.sign[n] > 0: # from left
                # Må ha (i-1,j) på land og (i,j) = sjø¸
                if M[j,i-1]: river_status =  '\n'.join([river_status,  "Error with river, source {} from sea cell".format(riv.riverno[n])])
                if not M[j,i]: river_status = '\n'.join([river_status, "Error with river, source {} to land cell".format(riv.riverno[n])])
                river_status = '\n'.join([river_status, "grid cell: %6d %7d %8s %7d %8s %10.1f %6d %6d\n" % ( riv.riverno[n], i,"", j,"", H[j,i], riv.direction[n], riv.sign[n])])
            else:
                # Må ha (i,j) på land og (i-1,j) på sjø¸
                if M[j,i]:   river_status =  '\n'.join([river_status,  "Error with river, source {} from sea cell".format(riv.riverno[n])])
                if not M[j,i-1]: river_status = '\n'.join([river_status, "Error with river, source {} to land cell".format(riv.riverno[n])])
                river_status = '\n'.join([river_status, "grid cell: %6d %7d %8s %7d %8s %10.1f %6d %6d\n" % (riv.riverno[n], i,"", j,"", H[j,i], riv.direction[n], riv.sign[n])])
        else: # V-point
            if riv.sign[n] > 0: # "up"-wards
                # Må ha (i,j-1) på land og (i,j) på sjø¸
                if M[j-1,i]:    river_status =  '\n'.join([river_status,  "Error with river, source {} from sea cell".format(riv.riverno[n])])
                if not M[j,i]: river_status = '\n'.join([river_status, "Error with river, source {} to land cell".format(riv.riverno[n])])
                river_status = '\n'.join([river_status, "grid cell: %6d %7d %8s %7d %8s %10.1f %6d %6d\n" % (riv.riverno[n], i,"", j,"", H[j,i], riv.direction[n], riv.sign[n])])
            else:
                # Må ha (i,j) på land og (i,j-1) på sjø¸
                if M[j,i]:       river_status =  '\n'.join([river_status,  "Error with river, source {} from sea cell".format(riv.riverno[n])])
                if not M[j-1,i]:  river_status = '\n'.join([river_status, "Error with river, source {} to land cell".format(riv.riverno[n])])
                river_status = '\n'.join([river_status, "grid cell: %6d %7d %8s %7d %8s %10.1f %6d %6d\n" % ( riv.riverno[n], i,"", j,"", H[j,i], riv.direction[n], riv.sign[n])])
    return river_status
