---
layout: default
---

# C++11 pointerek, new/delete kerülése

Egy rövid példa shared, unique és weak pointerre, make_shared, make_unique (C++14!).

Unique és weak: Foltok, valamint egy aktuális kijelölt (ami alól törlődhet a folt).

Shared: valami gráfos reprezentáció?

Közben referencia átadás


*Lásd alkalmazasfejesztes repo: Cpp11Pointers, hivatkozzam is!*

    #include <iostream>
    #include <vector>
    #include <memory>

    using namespace std;

    class Blob
    {
    public:
        Blob(int x, int y)
            : x(x), y(y)
        {
        }

    public:
        int x,y;
    };

    void show(std::weak_ptr<Blob>& blob)
    {
        std::shared_ptr<Blob> lockedBlob = blob.lock();

        if (lockedBlob)
        {
            cout << "Blob(" << lockedBlob->x << "," << lockedBlob->y << ")" << endl;
        }
        else
        {
            cout << "Blob does not exist anymore." << endl;
        }
    }

    int main()
    {
        // Creating two containers
        std::vector<std::shared_ptr<Blob>> container0;
        std::vector<std::shared_ptr<Blob>> container1;
        // Adding a blob to both of them
        std::shared_ptr<Blob> newBlob = std::make_shared<Blob>(12,34);
        container0.push_back(newBlob);
        container1.push_back(newBlob);
        // Adding another blob to one of them
        newBlob = std::make_shared<Blob>(56,78);
        container0.push_back(newBlob);

        // Storing a weak pointer to the blob contained in
        //  both containers
        std::weak_ptr<Blob> selectedBlob = (std::shared_ptr<Blob>)container1[0];

        // Successively clearing the containers and accessing the selected blob.
        show(selectedBlob); // Shows Blob(12,34)
        container1.clear();
        show(selectedBlob); // Shows Blob(12,34)
        container0.clear();
        show(selectedBlob); // Blob(12,34) does not exist anymore

        cout << "Finished." << endl;
    }

*alkalmazasfejlesztes Cpp11UniqueAndLambda, hivatkozzam is!*

    #include <iostream>
    #include <vector>
    #include <memory>
    #include <functional>

    using namespace std;

    // Some kind of blob we need to store.
    class Blob
    {
    public:
        Blob(int x, int y)
            : x(x), y(y)
        {
        }

    public:
        int x,y;
    };

    // Stores blobs
    class BlobContainer
    {
    public:
        void add(std::unique_ptr<Blob>& newBlob)
        {
            // Cannot simply copy, we need to move.
            blobs.push_back(std::move(newBlob));
        }

        // Execute a lambda on all stored elements
        void ForEach(std::function<void(const Blob&)> lambda )
        {
            for(const auto& blob : blobs)
            {
                lambda(*blob);
            }
        }

    private:
    	// This is where we store the blobs
    	std::vector<std::unique_ptr<Blob>> blobs;
    };
    
    // To make the output easier
    std::ostream& operator<<(std::ostream& stream, const Blob& blob)
    {
	    stream << "Blob(" << blob.x << "," << blob.y << ")";
	    return stream;
    }
    
    int main()
    {
    	// Create a set of blobs (which takes ownership)
    	BlobContainer blobs;
    
    	// Add 2 blobs
    	std::unique_ptr<Blob> newBlob = std::make_unique<Blob>(12,34);
    	blobs.add(newBlob);
    	newBlob = std::make_unique<Blob>(56,78);
    	blobs.add(newBlob);
    
    	// After adding, the newBlob pointer is null, as the ownership has moved
    	//  into the container.
    	cout << ( newBlob ? "newBlob is still valid" : "newBlob is invalid" ) << endl;
    
    	cout << "Contents:" << endl;
    	blobs.ForEach( [](const Blob& blob){ cout << blob << endl; } );
    }
    