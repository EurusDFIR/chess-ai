#include "transposition.h"
#include <cstring>
#include <algorithm>

TranspositionTable::TranspositionTable(size_t sizeMB)
    : sizeMB(0), numEntries(0), currentAge(0), hits(0), misses(0), collisions(0)
{
    resize(sizeMB);
}

void TranspositionTable::resize(size_t sizeMB)
{
    this->sizeMB = sizeMB;

    // Calculate number of entries
    size_t sizeBytes = sizeMB * 1024 * 1024;
    numEntries = sizeBytes / sizeof(TTEntry);

    // Resize table
    table.clear();
    table.resize(numEntries);

    // Reset statistics
    hits = 0;
    misses = 0;
    collisions = 0;
    currentAge = 0;
}

bool TranspositionTable::probe(uint64_t hash, int depth, Score alpha, Score beta, TTEntry &entry)
{
    size_t index = getIndex(hash);
    const TTEntry &stored = table[index];

    // Check if entry exists and matches
    if (stored.hash != hash)
    {
        misses++;
        return false;
    }

    // Entry found
    hits++;
    entry = stored;

    // Check if depth is sufficient
    if (stored.depth < depth)
    {
        return false;
    }

    // Check if score is useful
    Score score = stored.score;

    switch (stored.flag)
    {
    case TT_EXACT:
        // Exact score, always useful
        return true;

    case TT_ALPHA:
        // Upper bound
        if (score <= alpha)
        {
            entry.score = alpha;
            return true;
        }
        break;

    case TT_BETA:
        // Lower bound
        if (score >= beta)
        {
            entry.score = beta;
            return true;
        }
        break;
    }

    // Score not useful for cutoff, but move might be useful
    return false;
}

void TranspositionTable::store(uint64_t hash, const Move &bestMove, Score score, int depth, uint8_t flag)
{
    size_t index = getIndex(hash);
    TTEntry &entry = table[index];

    // Replace if:
    // 1. Entry is empty (hash == 0)
    // 2. Same position (hash matches)
    // 3. Deeper search
    // 4. Older entry
    bool replace = (entry.hash == 0) ||
                   (entry.hash == hash) ||
                   (depth >= entry.depth) ||
                   (entry.age != currentAge);

    if (replace)
    {
        if (entry.hash != 0 && entry.hash != hash)
        {
            collisions++;
        }

        entry.hash = hash;
        entry.bestMove = bestMove;
        entry.score = score;
        entry.depth = depth;
        entry.flag = flag;
        entry.age = currentAge;
    }
}

void TranspositionTable::clear()
{
    std::fill(table.begin(), table.end(), TTEntry());
    hits = 0;
    misses = 0;
    collisions = 0;
    currentAge = 0;
}
