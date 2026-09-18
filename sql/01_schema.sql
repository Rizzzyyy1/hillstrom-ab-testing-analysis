/* PostgreSQL schema for flat Hillstrom experiment data. No customer ID exists. */
CREATE TABLE IF NOT EXISTS hillstrom (
    recency integer NOT NULL CHECK (recency >= 1),
    history_segment text NOT NULL, history numeric(12,2) NOT NULL CHECK (history >= 0),
    mens smallint NOT NULL CHECK (mens IN (0,1)), womens smallint NOT NULL CHECK (womens IN (0,1)),
    zip_code text NOT NULL, newbie smallint NOT NULL CHECK (newbie IN (0,1)), channel text NOT NULL,
    segment text NOT NULL CHECK (segment IN ('No E-Mail','Mens E-Mail','Womens E-Mail')),
    visit smallint NOT NULL CHECK (visit IN (0,1)), conversion smallint NOT NULL CHECK (conversion IN (0,1)),
    spend numeric(12,2) NOT NULL CHECK (spend >= 0)
);
COMMENT ON TABLE hillstrom IS 'Flat experiment table; rows are not verified unique customers.';
