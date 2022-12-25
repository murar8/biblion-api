from datetime import datetime
from uuid import UUID


posts_seed = [
    {
        "_id": "a46yh2d3",
        "creator": UUID("f4c8e142-5a8e-4759-9eec-74d9139dcfd5"),
        "content": "console.log('Hello, world!')",
        "name": "hello.js",
        "language": "js",
        "createdAt": datetime(2002, 10, 27, 2, 0, 0),
        "updatedAt": datetime(2002, 10, 28, 14, 0, 0),
    },
    {
        "_id": "bdu764rt",
        "creator": UUID("f4c8e142-5a8e-4759-9eec-74d9139dcfd5"),
        "content": "Hello, world!",
        "name": "hello.txt",
        "language": "txt",
        "createdAt": datetime(2002, 10, 27, 6, 0, 0),
        "updatedAt": datetime(2002, 10, 28, 11, 0, 0),
    },
    {
        "_id": "ctrdg53d",
        "creator": UUID("34b8028f-a220-498e-85c9-7304e44cb272"),
        "content": "console.log('Hello, world!')",
        "name": "test.ts",
        "language": "ts",
        "createdAt": datetime(2002, 10, 27, 3, 0, 0),
        "updatedAt": datetime(2002, 10, 28, 22, 0, 0),
    },
    {
        "_id": "d7yhmbr5",
        "creator": UUID("34b8028f-a220-498e-85c9-7304e44cb272"),
        "content": "Hello, world!",
        "name": "hi.txt",
        "language": "txt",
        "createdAt": datetime(2002, 10, 27, 1, 0, 0),
        "updatedAt": datetime(2002, 10, 28, 18, 0, 0),
    },
]


users_seed = [
    {
        "_id": UUID("f4c8e142-5a8e-4759-9eec-74d9139dcfd5"),
        "email": "mrbrown@user.com",
        "name": "mr_brown",
        "passwordHash": (
            # password: "hastasiempre"
            b"$2b$12$AccWeQEg2szEkty9YCWLa.1Y2snNhc.DTmk97Qveg8hpDgm9.O2kG"
        ),
        "verified": True,
        "createdAt": datetime(2002, 10, 27, 2, 0, 0),
        "updatedAt": datetime(2002, 10, 28, 14, 0, 0),
    },
    {
        "_id": UUID("34b8028f-a220-498e-85c9-7304e44cb272"),
        "email": "mrgreen@user.com",
        "name": "mr_green",
        "passwordHash": (
            # password: "hastanunca"
            b"$2b$12$tToXPOgFqXrqjuIdCXODZeXK0IfL.kz7sZ1/SxWRvN3Zn.TZYe7MW"
        ),
        "verified": False,
        "createdAt": datetime(2002, 10, 27, 2, 0, 0),
        "updatedAt": datetime(2002, 10, 28, 14, 0, 0),
    },
    {
        "_id": UUID("af71f215-c3f8-441f-9498-e75f8dfbcf4b"),
        "email": "mrred@user.com",
        "name": "mr_red",
        "passwordHash": (
            # password: "hastacuando"
            b"$2b$12$yp9ipcT4VdpkMmwSNTaoied19ElSKuKtjeONj.7.nb5HUZllHvMx."
        ),
        "verified": False,
        "createdAt": datetime(2002, 10, 22, 2, 0, 0),
        "updatedAt": datetime(2002, 11, 28, 14, 0, 0),
        "verificationCode": UUID("03d06d59-5fd5-4c49-bafe-91bab21d1391"),
        "verificationCodeIat": datetime.now(),
        "resetCode": UUID("6e94e45a-5f47-4b38-9483-6b1d5d57266b"),
        "resetCodeIat": datetime.now(),
    },
]
