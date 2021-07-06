#!/usr/bin/env ruby
require 'json'
require 'csv'
require 'optparse'

class ExpChains
    def self.generate(options)
        symbolinfo_file = File.open(options[:symbolinfo], "r")
        symbolinfo = JSON.load(symbolinfo_file)
        symbolinfo_file.close()

        exp_chain = generate_from_symbolinfo(symbolinfo)

        if options[:merge] && File.exist?(options[:merge])
            old_exp_chain = read_expchain(options[:merge])
            exp_chain = old_exp_chain.merge(exp_chain) do |key, old, new|
                v = new.clone
                v['rts_ticker'] = old['rts_ticker']
                v
            end
        end

        write_expchain(options[:expchain], exp_chain)
    end

    def self.compiletab(options)
        p = File.join(options[:path], "**", "*.csv")

        tab_content = {}

        if options[:merge]
            tab_content = read_tabfile(options[:merge])
        end

        Dir.glob(p) do |file|
            exp_chain = read_expchain(file)
            tab_content.merge! expchain_to_tab(exp_chain)
        end

        File.open(options[:tabfile], "w") do |f|
            tab_content.each do |t, e|
                if ! (e == "delete" || e == "remove")
                    f.write("#{t.ljust(16)} #{e}\n")
                end
            end
        end
    end


    def self.generate_from_symbolinfo(symbolinfo)
        symbols = symbolinfo['symbol']
        if !symbols.kind_of?(Array)
            symbols = [symbols]
        end
        tickers = symbolinfo['ticker']
        expirations = symbolinfo['expiration']
        roots = symbolinfo['root']

        exp_chain = {}

        symbols.each_with_index do |s, i|
            t = tickers.kind_of?(Array) ? tickers[i] : tickers
            e = expirations.kind_of?(Array) ? expirations[i] : expirations
            r = roots.kind_of?(Array) ? roots[i] : roots
            dbc_ticker, rts_ticker = parse_ticker(t)
            dbc_ticker = norm_dbc_ticker(dbc_ticker)
            exp_chain[s] = {
                'symbol' => s,
                'dbc_ticker' => dbc_ticker,
                'rts_ticker' => rts_ticker,
                'root' => r,
                'expiration' => e.to_s,
            }
        end
        return exp_chain
    end

    def self.parse_ticker(t)
        parts = t.split('~')
        return parts[0], parts[2]
    end

    def self.norm_dbc_ticker(t)
        re_common = /^(?<root>[A-Z0-9_]+) (?<month>[A-Z])(?<year>[0-9]{2})(?<session>=[0-9]+)?(?<exchange>-[A-Z0-9]+)?$/
        m = re_common.match(t)
        if m
            return "#{m['root']} #{m['month']}20#{m['year']}#{m['session']}#{m['exchange']}"
        end
        re_with_day = /^(?<root>[A-Z0-9_]+) (?<year>[0-9]{2})(?<month>[A-Z])(?<day>[0-9]{2})?(?<session>=[0-9]+)?(?<exchange>-[A-Z0-9]+)?$/
        m = re_with_day.match(t)
        if m
            return "#{m['root']} 20#{m['year']}#{m['month']}#{m['day']}#{m['session']}#{m['exchange']}"
        end
        return t
    end

    def self.symbol_prop_from_csv_line(l)
        return {
            'symbol'     => l[0],
            'dbc_ticker' => l[1],
            'rts_ticker' => l[2],
            'root'       => l[3],
            'expiration' => l[4],
        }
    end

    def self.symbol_prop_to_csv_line(p)
        return [p['symbol'], p['dbc_ticker'], p['rts_ticker'], p['root'], p['expiration']]
    end

    def self.read_expchain(filename)
        lines = CSV.read(filename)
        exp_chain = {}
        lines.each do |l|
            p = symbol_prop_from_csv_line(l)
            exp_chain[p['symbol']] = p
        end
        return exp_chain
    end

    def self.write_expchain(filename, exp_chain)
        symbol_props = exp_chain.values
        symbol_props.sort_by{|p| [p['root'], p['expiration']] }
        CSV.open(filename, "w") do |csv|
            symbol_props.each do |p|
                csv << symbol_prop_to_csv_line(p)
            end
        end
    end

    def self.expchain_to_tab(exp_chain)
        symbol_props = exp_chain.values
        tab = {}
        symbol_props.each do |p|
            tab[p['dbc_ticker']] = convert_expiration_to_tab(p['expiration'])
        end
        return tab
    end

    def self.convert_expiration_to_tab(expiration)
        if expiration == "delete" || expiration == "remove"
            return expiration
        end
        year = expiration[0, 4]
        month = expiration[4,2]
        day = expiration[6, 2]
        day[0] = " " if day[0] == "0"
        month[0] = " " if month[0] == "0"
        return "#{month}/#{day}/#{year}"
    end

    def self.read_tabfile(filename)
        tab_content = {}
        File.open(filename, "r").each do |line|
            line.strip!
            exp = line[line.length-10,10]
            dbc_ticker = line[0,line.length-10].strip
            tab_content[dbc_ticker] = exp
        end
        return tab_content
    end

end

if __FILE__ == $0
    begin
        options = {}
        global = OptionParser.new do |opts|
        end
        subcommands = {
            'generate' => OptionParser.new do |opts|
                opts.on("-s SYMBOLINFO", "--symbolinfo SYMBOLINFO", "symbolinfo file path") do |v|
                    options[:symbolinfo] = v
                end
                opts.on("-e EXPCHAIN", "--expchain EXPCHAIN", "expchain file") do |v|
                    options[:expchain] = v
                end
                opts.on("-m MERGE_EXPCHAIN", "--merge MERGE_EXPCHAIN", "old expchain file") do |v|
                    options[:merge] = v
                end
            end,
            'compiletab' => OptionParser.new do |opts|
                opts.on("-t TABFILE", "--tabfile TABFILE", "path to new tabfile") do |v|
                    options[:tabfile] = v
                end
                opts.on("-p EXPCHAINS_PATH", "--path EXPCHAINS_PATH", "path to expchains directory") do |v|
                    options[:path] = v
                end
                opts.on("-m MERGE_TABFILE", "--merge MERGE_TABFILE", "old tab file") do |v|
                    options[:merge] = v
                end
            end,
        }

        global.order!
        command = ARGV.shift
        options[:command] = command
        subcommands[command].order!

        case command
        when 'generate'
            ExpChains.generate(options)
        when 'compiletab'
            ExpChains.compiletab(options)
        end

    rescue SystemExit => e
        raise e
    rescue Exception => e
        abort("expchains failed with error: #{e.message}, #{e.backtrace.inspect}")
    end
end
