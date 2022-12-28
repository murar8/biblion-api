# pylint: disable=line-too-long

from datetime import datetime
from uuid import UUID

from app.models.documents import PostDocument, UserDocument


async def init_db():
    """
    Initialize the test environment with some initial values.
    Note: This should be called after the app startup event is executed.
    """
    await PostDocument.delete_all()
    await UserDocument.delete_all()

    await UserDocument.insert_many(
        [
            UserDocument(
                id=UUID("f4c8e142-5a8e-4759-9eec-74d9139dcfd5"),
                createdAt=datetime(2002, 10, 27, 2, 0, 0),
                email="mrbrown@user.com",
                name="mr_brown",
                passwordHash=b"$2b$12$AccWeQEg2szEkty9YCWLa.1Y2snNhc.DTmk97Qveg8hpDgm9.O2kG",  # password: "hastasiempre"
                updatedAt=datetime(2002, 10, 28, 14, 0, 0),
                verified=True,
            ),
            UserDocument(
                id=UUID("34b8028f-a220-498e-85c9-7304e44cb272"),
                createdAt=datetime(2002, 10, 27, 2, 0, 0),
                email="mrgreen@user.com",
                name="mr_green",
                passwordHash=b"$2b$12$tToXPOgFqXrqjuIdCXODZeXK0IfL.kz7sZ1/SxWRvN3Zn.TZYe7MW",  # password: "hastanunca"
                updatedAt=datetime(2002, 10, 28, 14, 0, 0),
                verified=False,
            ),
            UserDocument(
                id=UUID("af71f215-c3f8-441f-9498-e75f8dfbcf4b"),
                createdAt=datetime(2002, 10, 22, 2, 0, 0),
                email="mrred@user.com",
                name="mr_red",
                passwordHash=b"$2b$12$yp9ipcT4VdpkMmwSNTaoied19ElSKuKtjeONj.7.nb5HUZllHvMx.",  # password: "hastacuando"
                resetCode=UUID("6e94e45a-5f47-4b38-9483-6b1d5d57266b"),
                resetCodeIat=datetime.now(),
                updatedAt=datetime(2002, 11, 28, 14, 0, 0),
                verificationCode=UUID("03d06d59-5fd5-4c49-bafe-91bab21d1391"),
                verificationCodeIat=datetime.now(),
                verified=False,
            ),
        ]
    )

    await PostDocument.insert_many(
        [
            PostDocument(
                id="a46yh2d3",
                content="console.log('Hello, world!')",
                createdAt=datetime(2002, 10, 27, 2, 0, 0),
                creator=UUID("f4c8e142-5a8e-4759-9eec-74d9139dcfd5"),
                language="jsx",
                name="hello.js",
                updatedAt=datetime(2002, 10, 28, 14, 0, 0),
            ),
            PostDocument(
                id="bdu764rt",
                content="Hello, world!",
                createdAt=datetime(2002, 10, 27, 6, 0, 0),
                creator=UUID("f4c8e142-5a8e-4759-9eec-74d9139dcfd5"),
                name="hello.txt",
                updatedAt=datetime(2002, 10, 28, 11, 0, 0),
            ),
            PostDocument(
                id="ctrdg53d",
                content="console.log('Hello, world!')",
                createdAt=datetime(2002, 10, 27, 3, 0, 0),
                creator=UUID("34b8028f-a220-498e-85c9-7304e44cb272"),
                language="tsx",
                name="test.ts",
                updatedAt=datetime(2002, 10, 28, 22, 0, 0),
            ),
            PostDocument(
                id="d7yhmbr5",
                content="Hello, world!",
                createdAt=datetime(2002, 10, 27, 1, 0, 0),
                creator=UUID("34b8028f-a220-498e-85c9-7304e44cb272"),
                name="hi.txt",
                updatedAt=datetime(2002, 10, 28, 18, 0, 0),
            ),
        ]
    )
