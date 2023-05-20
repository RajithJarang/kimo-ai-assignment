def rating_pipeline(rating):
    return [
        {
            "$inc": {
                "chapters.$.rating.total_ratings": 1,
                "chapters.$.rating.positive_ratings": 1 if rating else 0,
                "chapters.$.rating.negative_ratings": 1 if not rating else 0,
            }
        },
        {
            '$unwind': {
                'path': '$chapters',
                'includeArrayIndex': 'true'
            }
        }, {
            '$group': {
                '_id': '$_id',
                'positive_rating': {
                    '$sum': '$chapters.rating.positive_ratings'
                },
                'negative_rating': {
                    '$sum': '$chapters.rating.negative_ratings'
                },
                'total_rating': {
                    '$sum': '$chapters.rating.total_ratings'
                }
            }
        }, {
            '$set': {
                'rating': {
                    '$cond': {
                        'if': {
                            '$eq': [
                                '$total_rating', 0
                            ]
                        },
                        'then': 0,
                        'else': {
                            '$divide': [
                                {
                                    '$subtract': [
                                        '$positive_rating', '$negative_rating'
                                    ]
                                }, '$total_rating'
                            ]
                        }
                    }
                }
            }
        },
        {
            '$project': {
                'rating': 1
            }
        },
    ]
