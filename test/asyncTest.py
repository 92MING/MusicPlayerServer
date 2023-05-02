import asyncio
import threading

async def testWait():
    for i in range(5):
        print('testWait',i)
        await asyncio.sleep(1)
    return (1,2)
async def testWait2():
    print('testWait2')
    await asyncio.sleep(2)
    print('testWait2 end')
    return 3

async def run():
    print('run')
    #get result of testWait and testWait2, wait for all
    (x,y),z = await asyncio.gather(testWait(), testWait2())
    print(x,y,z)

    print('run end')

if __name__ == '__main__':
    def f():
        x = asyncio.run(testWait())
        print(x)
    f()


