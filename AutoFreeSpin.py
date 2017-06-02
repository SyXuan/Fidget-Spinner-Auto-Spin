import os
import sys
import time
import re
import subprocess
import traceback

delay = 0.2


def main():
    print ('\nStart AutoFreeSpin for Fidget Spinner\n')
    time.sleep(delay)

    targetDevice = getTargetDevice()
    dpi = getDpi(targetDevice)

    print('How many loop do you want?')
    select = input('>>> Input [default:1000]: ') or '1000'
    loop = int(select)

    i = 0
    while i < loop:
        i += 1
        print('Count %d/%d' % (i, loop))
        swipeButton(targetDevice, dpi)
        time.sleep(delay)

    os.system('pause')


# Select target device from adb devices list
def getTargetDevice():
    # Get the adb shell output
    adbShell = ['adb', 'devices']
    try:
        proc = subprocess.Popen(adbShell, shell=False, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        out = decode(out)
        # print out
    except Exception:
        print('Error trying to launch ADB:\n\n%s\n\n%s' %
              (adbShell, traceback.format_exc()))
        os.system('pause')
    # Get list of device ids
    deviceList = []
    for line in out.split('\n'):
        line = line.strip()
        if line.endswith('device'):
            deviceList.append(re.sub(r'[ \t]*device$', '', line))
    # Build menu options displaying name, version, and device id
    adbViews = []
    options = []
    for view in adbViews:
        options.append([view.name, 'Focus existing view'])
    for device in deviceList:
        # dump
        adbShell = ['adb', '-s', device, 'shell', 'cat /system/build.prop']
        proc = subprocess.Popen(adbShell, shell=False, stdout=subprocess.PIPE)
        build_prop = decode(proc.stdout.read().strip())
        # get name
        product = 'Unknown'  # should never actually see this
        if device.startswith('emulator'):
            port = int(device.rsplit('-')[-1])
            t = telnetlib.Telnet('localhost', port)
            t.read_until(b'OK', 1000).decode('utf-8')
            t.write(b'avd name\n')
            product = t.read_until(b'OK', 1000).decode('utf-8')
            t.close()
            product = product.replace('OK', '').strip()
        else:
            product = re.findall(
                r'^ro\.product\.model=(.*)$', build_prop, re.MULTILINE)
            if product:
                product = product[0]
        # get version
        version = re.findall(
            r'ro\.build\.version\.release=(.*)$', build_prop, re.MULTILINE)
        if version:
            version = version[0]
        else:
            version = 'x.x.x'
        # append to list
        product = str(product).strip()
        version = str(version).strip()
        device = str(device).strip()
        options.append('%s %s - %s' % (product, version, device))
    # Select devices
    if len(options) == 0:
        print('ADB: No device attached!')
        os.system('pause')
        sys.exit()
    num = 0
    print('Select devices:')
    for idx, val in enumerate(options):
        num = num + 1
        print('[%d]' % num, val)
    targetDevice = None
    while targetDevice is None:
        try:
            select = input('>>> Input [default:1]: ') or '1'
            targetDevice = deviceList[int(select) - 1]
        except Exception:
            print('Please input the number in list\n')
    print('Target device:', targetDevice)
    print('...')
    return targetDevice


def getDpi(targetDevice):
    # adbShell = 'adb -s %s shell dumpsys window displays | grep dpi' % targetDevice
    # For windows and linux
    adbShell = 'adb -s %s shell dumpsys window displays' % targetDevice
    adbTmp = os.popen(adbShell).read()
    adbTmp = grep(adbTmp, 'dpi')
    # import re to find number
    dpi = re.findall('\d+dpi', adbTmp)
    dpi = (re.findall('\d+', dpi[0]))[0]
    print('Device dpi =', dpi, '\n')
    return int(dpi)

def swipeButton(targetDevice, dpi):
    mul = dpi / 160
    x1 = 60 * mul
    x2 = 300 * mul
    y = 480 * mul
    # print 'mul = %d, btn = %d' % (mul, btn)
    print('>> Swipe creen from %d,%d to %d,%d' % (x1, y, x2, y))

    adbShell = 'adb -s %s shell input swipe %d %d %d %d' % (targetDevice, x1, y, x2, y)
    os.popen(adbShell)


def grep(s, pattern):
    return '\n'.join(re.findall(r'^.*%s.*?$' % pattern, s, flags=re.M))


def decode(ind):
    try:
        return ind.decode('utf-8')
    except Exception:
        try:
            return ind.decode(sys.getdefaultencoding())
        except Exception:
            return ind


if __name__ == '__main__':
    main()
