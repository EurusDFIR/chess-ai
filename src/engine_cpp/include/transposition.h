#ifndef TRANSPOSITION_H
#define TRANSPOSITION_H

#include "types.h"
#include <vector>

// Transposition Table entry
struct TTEntry
{
    uint64_t hash;
    Move bestMove;
    Score score;
    int depth;
    uint8_t flag; // TT_EXACT, TT_ALPHA, TT_BETA
    uint8_t age;

    TTEntry() : hash(0), bestMove(), score(0), depth(0), flag(0), age(0) {}
};

class TranspositionTable
{
private:
    std::vector<TTEntry> table;
    size_t sizeMB;
    size_t numEntries;
    uint8_t currentAge;

    // Statistics
    uint64_t hits;
    uint64_t misses;
    uint64_t collisions;

public:
    TranspositionTable(size_t sizeMB = 256);
    ~TranspositionTable() = default;

    // Resize table
    void resize(size_t sizeMB);

    // Probe table
    bool probe(uint64_t hash, int depth, Score alpha, Score beta, TTEntry &entry);

    // Store entry
    void store(uint64_t hash, const Move &bestMove, Score score, int depth, uint8_t flag);

    // Clear table
    void clear();

    // Age management
    void incrementAge() { currentAge++; }
    uint8_t getAge() const { return currentAge; }

    // Statistics
    uint64_t getHits() const { return hits; }
    uint64_t getMisses() const { return misses; }
    uint64_t getCollisions() const { return collisions; }
    double getHitRate() const
    {
        uint64_t total = hits + misses;
        return total > 0 ? (double)hits / total : 0.0;
    }

    // Get table size
    size_t getSizeMB() const { return sizeMB; }
    size_t getNumEntries() const { return numEntries; }

private:
    size_t getIndex(uint64_t hash) const { return hash % numEntries; }
};

#endif // TRANSPOSITION_H
